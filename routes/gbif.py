from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import auth_middleware
from gbif.client import (
    search_species, 
    get_species, 
    get_taxonomy_from_otol,
    get_occurrences_from_gbif,
    extract_ecological_zones_from_gbif_occurrences
)
from gbif.normalizer import normalize_species
from gbif.importer import import_species
from gbif.zones_handler import import_ecological_zones_with_species

router = APIRouter()

class GBIFRequest(BaseModel):
    name: str
    country: str = "MX"  # Por defecto México


@router.post("/import")
def import_from_gbif(
    body: GBIFRequest,
    _=Depends(auth_middleware)
):
    found = search_species(body.name)

    if not found:
        raise HTTPException(404, "Species not found in GBIF")

    gbif_key = found["key"]
    full_data = get_species(gbif_key)
    
    print("\n" + "="*60)
    print("=== DATOS BRUTOS DE LA API GBIF ===")
    print(f"Respuesta completa: {full_data}")
    print(f"phylum: {full_data.get('phylum')}")
    print(f"class: {full_data.get('class')}")
    print(f"order: {full_data.get('order')}")
    print(f"family: {full_data.get('family')}")
    print(f"genus: {full_data.get('genus')}")
    print("="*60)
    
    # Obtener taxonomía completa desde OpenTreeOfLife
    scientific_name = full_data.get("scientificName")
    print(f"\n🔍 Consultando OpenTreeOfLife por: {scientific_name}")
    otol_data = get_taxonomy_from_otol(scientific_name)
    
    print("\n" + "="*60)
    print("=== DATOS DE OPENTREEOFLIFE ===")
    print(f"phylum: {otol_data.get('phylum')}")
    print(f"class: {otol_data.get('class')}")
    print(f"order: {otol_data.get('order')}")
    print(f"family: {otol_data.get('family')}")
    print(f"genus: {otol_data.get('genus')}")
    print("="*60)

    normalized = normalize_species(full_data, otol_data)
    print("\n" + "="*60)
    print("=== DATOS NORMALIZADOS (COMBINADOS) ===")
    print(normalized)
    print(f"phylum normalizado: {normalized.get('phylum')}")
    print(f"class_name normalizado: {normalized.get('class_name')}")
    print(f"order_name normalizado: {normalized.get('order_name')}")
    print(f"family normalizado: {normalized.get('family')}")
    print(f"genus normalizado: {normalized.get('genus')}")
    print("="*60 + "\n")
    
    result = import_species(normalized)
    
    # Obtener ID de especie que fue creado
    from app.db import get_connection
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id_species FROM species WHERE taxonKey=%s", (gbif_key,))
        row = cur.fetchone()
        id_species = row["id_species"] if row else None
    conn.close()
    
    if not id_species:
        raise HTTPException(500, "Error: No se pudo recuperar id_species después de importar")
    
    # Obtener ocurrencias de GBIF con paginación
    print(f"\n📍 Obteniendo ocurrencias de GBIF para {body.country}...")
    
    # Convertir país a código ISO si es necesario
    country_code = "MX" if body.country.lower() in ["mexico", "méxico"] else body.country
    
    occurrences = get_occurrences_from_gbif(gbif_key, limit=300, country_code=country_code)
    
    if occurrences and len(occurrences) > 0:
        print(f"✓ Se encontraron {len(occurrences)} ocurrencias con coordenadas")
        zones_data = extract_ecological_zones_from_gbif_occurrences(occurrences)
        zones_result = import_ecological_zones_with_species(zones_data, gbif_key, id_species)
    else:
        print(f"⚠️ No hay ocurrencias con coordenadas para {body.country}")
        zones_result = {
            "zones_inserted": 0,
            "zones_skipped": 0,
            "species_zones_linked": 0,
            "occurrences_inserted": 0,
            "occurrences_duplicated": 0,
            "occurrences_errors": 0,
            "errors": 0
        }

    return {
        "query": body.name,
        "taxonKey": gbif_key,
        "scientific_name": normalized["scientific_name"],
        "species_import": result,
        "ecological_zones_import": zones_result,
        "zones_source": "GBIF"
    }
