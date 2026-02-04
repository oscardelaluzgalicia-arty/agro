import requests

GBIF_URL = "https://api.gbif.org/v1"
OTOL_URL = "https://api.opentreeoflife.org/v3"
INATURALIST_URL = "https://api.inaturalist.org/v1"

def get_occurrence_taxon_key(species):
    return species["key"] if species["rank"] == "SPECIES" else species["usageKey"]

def search_species(name: str):
    """
    Busca una especie en GBIF por nombre común o científico
    """
    try:
        print(f"\n🔍 Buscando especie: {name}")

        match = match_species(name)

        if match:
            rank = match.get("rank")
            confidence = match.get("confidence", 0)
            status = match.get("status")

            print(
                f"Match: {match.get('scientificName')} | "
                f"rank={rank} | confidence={confidence}"
            )

            if (
                match.get("usageKey")
                and rank == "SPECIES"
                and confidence >= 90
            ):
                key = match["usageKey"]

                try:
                    full = get_species(key)
                    print(f"✓ Taxón aceptado: key={key}")
                    return full
                except Exception:
                    return match

            else:
                print(" Match no confiable, usando fallback search")

        # Fallback
        res = requests.get(
            f"{GBIF_URL}/species/search",
            params={"q": name, "limit": 10},
            timeout=10
        )
        res.raise_for_status()
        results = res.json().get("results", [])

        if results:
            for r in results:
                if r.get("rank") == "SPECIES":
                    print(f"✓ Fallback species: {r.get('scientificName')} ({r.get('key')})")
                    return r

            return results[0]

        print(" No se encontraron resultados")
        return None

    except Exception as e:
        print(f" Error en búsqueda: {e}")
        return None


def match_species(name: str):
    """
    Resuelve una especie a un taxonKey canónico usando GBIF (/species/match)
    """
    try:
        print(f"\n Resolviendo especie: {name}")

        res = requests.get(
            f"{GBIF_URL}/species/match",
            params={"name": name},
            timeout=10
        )
        res.raise_for_status()
        data = res.json()

        if "usageKey" in data:
            print(f"✓ Match: {data.get('scientificName')} (key: {data['usageKey']})")
            return data
        else:
            print(" No se pudo resolver la especie")
            return None

    except Exception as e:
        print(f" Error en match: {e}")
        return None


def get_species(gbif_key: int):
    res = requests.get(
        f"{GBIF_URL}/species/{gbif_key}",
        timeout=10
    )
    res.raise_for_status()
    return res.json()


def get_taxonomy_from_otol(scientific_name: str):
    """
    Obtiene la taxonomía completa (phylum, class, order, family, genus) 
    desde OpenTreeOfLife
    """
    try:
        # Buscar la especie en OTOL - debe ser POST con JSON
        res = requests.post(
            f"{OTOL_URL}/tnrs/match_names",
            json={"names": [scientific_name]},
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
        
        results = data.get("results", [])
        
        if not results:
            print(f" Sin resultados de OTOL")
            return {}
        
        first_result = results[0]
        matches = first_result.get("matches", [])
        
        if not matches:
            print(f" No se encontró '{scientific_name}' en OpenTreeOfLife")
            return {}
        
        match = matches[0]
        ott_id = match.get("taxon", {}).get("ott_id")
        
        if not ott_id:
            print(f" No se encontró ott_id en el match")
            return {}
        
        print(f"✓ Encontrado en OTOL con ott_id: {ott_id}")
        
        # Obtener la taxonomía completa con lineage
        res = requests.post(
            f"{OTOL_URL}/taxonomy/taxon_info",
            json={"ott_id": ott_id, "include_lineage": True},
            timeout=10
        )
        res.raise_for_status()
        taxon_data = res.json()
        
        print(f"📍 Datos del taxón con lineage: {taxon_data}")
        
        # Extraer taxonomía del lineage
        taxonomy = extract_taxonomy_from_lineage(taxon_data)
        taxonomy["ott_id"] = ott_id
        
        return taxonomy
        
    except Exception as e:
        print(f" Error consultando OpenTreeOfLife: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def extract_taxonomy_from_lineage(taxon_data: dict) -> dict:
    """
    Extrae phylum, class, order, family, genus del lineage de OTOL
    """
    taxonomy = {
        "phylum": None,
        "class": None,
        "order": None,
        "family": None,
        "genus": None,
    }
    
    lineage = taxon_data.get("lineage", [])
    
    for item in lineage:
        rank = item.get("rank", "").lower()
        name = item.get("name")
        
        if rank == "phylum" and taxonomy["phylum"] is None:
            taxonomy["phylum"] = name
        elif rank == "class" and taxonomy["class"] is None:
            taxonomy["class"] = name
        elif rank == "order" and taxonomy["order"] is None:
            taxonomy["order"] = name
        elif rank == "family" and taxonomy["family"] is None:
            taxonomy["family"] = name
        elif rank == "genus" and taxonomy["genus"] is None:
            taxonomy["genus"] = name
    
    print(f"\n Taxonomía extraída: {taxonomy}")
    return taxonomy


def get_occurrences(taxon_key: int, limit: int = 1000, country_code: str = "MX", state_province: str = None):
    """
    Obtiene ocurrencias (avistamientos) de una especie desde GBIF
    Limitado a un país y/o estado específico
    
    country_code: Código ISO del país (ej: 'MX' para México)
    state_province: Nombre del estado o provincia
    """
    try:
        print(f"\n Obteniendo ocurrencias para taxonKey: {taxon_key} en {country_code}")
        
        # Parámetros base
        params = {
            "taxonKey": taxon_key,
            "limit": limit,
            "offset": 0,
            "hasCoordinate": True,
            "country": country_code
        }
        
        # Añadir state_province si se proporciona
        if state_province:
            params["stateProvince"] = state_province
        
        # Primer intento: con coordenadas válidas
        res = requests.get(
            f"{GBIF_URL}/occurrence/search",
            params=params,
            timeout=30
        )
        res.raise_for_status()
        data = res.json()
        
        occurrences = data.get("results", [])
        total_count = data.get("count", 0)
        
        print(f"✓ Con coordenadas: {len(occurrences)} ocurrencias de {total_count} totales")
        
        # Si no hay resultados con coordenadas, intentar sin ese filtro
        if len(occurrences) == 0:
            print(f" No hay ocurrencias con coordenadas, intentando sin filtro...")
            
            # Quitar filtro de coordenadas
            params.pop("hasCoordinate")
            
            res = requests.get(
                f"{GBIF_URL}/occurrence/search",
                params=params,
                timeout=30
            )
            res.raise_for_status()
            data = res.json()
            
            occurrences = data.get("results", [])
            total_count = data.get("count", 0)
            
            print(f"✓ Sin filtro de coordenadas: {len(occurrences)} ocurrencias de {total_count} totales")
        
        if occurrences:
            # Mostrar resumen de datos disponibles
            states = set()
            habitats = set()
            with_coords = 0
            
            for occ in occurrences:
                if occ.get("stateProvince"):
                    states.add(occ.get("stateProvince"))
                if occ.get("habitat"):
                    habitats.add(occ.get("habitat"))
                if occ.get("decimalLatitude") and occ.get("decimalLongitude"):
                    with_coords += 1
            
            print(f"  - Estados: {len(states)}")
            print(f"  - Con coordenadas: {with_coords}/{len(occurrences)}")
            print(f"  - Hábitats únicos: {len(habitats)}")
        
        return occurrences
        
    except Exception as e:
        print(f" Error obteniendo ocurrencias: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_occurrences_from_gbif(taxon_key: int, limit: int = 300, country_code: str = "MX", state_province: str = None) -> list:
    """
    Obtiene ocurrencias de GBIF usando el endpoint occurrence/search
    Con paginación automática para obtener todos los registros con coordenadas
    
    country_code: Código ISO del país (ej: 'MX' para México)
    state_province: Nombre del estado o provincia
    """
    try:
        print(f"\n Obteniendo ocurrencias de GBIF para taxonKey: {taxon_key} en {country_code}")
        
        all_occurrences = []
        offset = 0
        total_fetched = 0
        occurrences_with_coords = 0
        
        # Primero, intentar sin filtro de país para debug
        print(f"Intento 1: Sin filtro de país...")
        res = requests.get(
            f"{GBIF_URL}/occurrence/search",
            params={
                "taxonKey": taxon_key,
                "limit": 1,
                "offset": 0
            },
            timeout=30
        )
        res.raise_for_status()
        data = res.json()
        total_global = data.get("count", 0)
        print(f"    Total de ocurrencias GLOBALES: {total_global}")
        
        # Ahora intenta con país
        print(f"Intento 2: Con filtro country={country_code}...")
        search_params = {
            "taxonKey": taxon_key,
            "country": country_code,
            "limit": 1,
            "offset": 0
        }
        if state_province:
            search_params["stateProvince"] = state_province

        res = requests.get(
            f"{GBIF_URL}/occurrence/search",
            params=search_params,
            timeout=30
        )
        res.raise_for_status()
        data = res.json()
        total_mexico = data.get("count", 0)
        print(f"    Total de ocurrencias en {country_code}: {total_mexico}")
        
        # Si hay resultados, proceder con paginación
        if total_mexico == 0:
            print(f"   No hay ocurrencias en {country_code}")
            print(f"   Intentando obtener todos los resultados globales y filtrar por país...")
            country_code = None  # Obtener todo y filtrar en código
        
        offset = 0
        
        while True:
            print(f"   Descargando registros offset={offset}...")
            
            params = {
                "taxonKey": taxon_key,
                "limit": limit,
                "offset": offset
            }
            
            if country_code:
                params["country"] = country_code
            if state_province:
                params["stateProvince"] = state_province
            
            res = requests.get(
                f"{GBIF_URL}/occurrence/search",
                params=params,
                timeout=30
            )
            res.raise_for_status()
            data = res.json()
            
            results = data.get("results", [])
            total_count = data.get("count", 0)
            
            if not results:
                print(f"  ✓ No hay más resultados")
                break
            
            # Filtrar solo aquellas con coordenadas válidas
            with_coords = [
                occ for occ in results 
                if occ.get("decimalLatitude") is not None 
                and occ.get("decimalLongitude") is not None
            ]
            
            # Si no usamos filtro de país, filtrar por country
            if not country_code:
                with_coords = [
                    occ for occ in with_coords
                    if occ.get("country", "").upper() in ["MEXICO", country_code]
                ]
            
            all_occurrences.extend(with_coords)
            occurrences_with_coords += len(with_coords)
            total_fetched += len(results)
            offset += limit
            
            # Mostrar progreso
            print(f"    ✓ {len(results)} registros, {len(with_coords)} con coordenadas (total: {occurrences_with_coords})")
            print(f"       ({total_fetched}/{total_count})")
            
            # Limitar a primeras 100,000 para no tardar demasiado
            if occurrences_with_coords >= 100000:
                print(f"Se alcanzó el límite de 100,000 ocurrencias")
                break
            
            # Si ya tenemos todos los resultados, romper
            if total_fetched >= total_count:
                break
        
        print(f"✓ GBIF: {len(all_occurrences)} ocurrencias CON COORDENADAS encontradas")
        return all_occurrences
        
    except Exception as e:
        print(f" Error obteniendo ocurrencias de GBIF: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def extract_ecological_zones_from_gbif_occurrences(occurrences: list) -> dict:
    """
    Procesa ocurrencias de GBIF para extraer zonas ecológicas ÚNICAS
    Agrupa por estado (state_province) para crear zonas temáticas
    """
    zones_data = {}
    
    print(f"\n Procesando {len(occurrences)} ocurrencias de GBIF...")
    
    # Agrupar por zona (estado)
    for occ in occurrences:
        try:
            country = occ.get("country", "Unknown")
            state = occ.get("stateProvince", "Unknown")
            
            zone_key = f"{country}|{state}"
            
            if zone_key not in zones_data:
                zones_data[zone_key] = {
                    "country": country,
                    "state": state,
                    "biome_type": "Unknown",
                    "climate_type": "Unknown",
                    "observation_count": 0
                }
            
            zones_data[zone_key]["observation_count"] += 1
                
        except Exception as e:
            print(f" Error procesando ocurrencia: {e}")
            continue
    
    print(f"✓ Se extrajeron {len(zones_data)} zonas ecológicas ÚNICAS")
    
    # Mostrar zonas extraídas
    for zone_key, zone_info in sorted(zones_data.items()):
        print(f"  - {zone_key}: {zone_info['observation_count']} observaciones")
    
    return {
        "zones": zones_data,
        "occurrences": occurrences
    }


def parse_occurrence(occurrence: dict, species_id: int) -> dict:
    """
    Parsea una ocurrencia de GBIF a formato compatible con la tabla occurrences
    """
    return {
        "gbif_occurrence_id": occurrence.get("key"),
        "id_species": species_id,
        "decimal_latitude": occurrence.get("decimalLatitude"),
        "decimal_longitude": occurrence.get("decimalLongitude"),
        "coordinate_uncertainty_meters": occurrence.get("coordinateUncertaintyInMeters"),
        "country": occurrence.get("country"),
        "state_province": occurrence.get("stateProvince"),
        "municipality": occurrence.get("municipality"),
        "locality": occurrence.get("locality"),
        "event_date": occurrence.get("eventDate"),
        "year": occurrence.get("year"),
        "month": occurrence.get("month"),
        "day": occurrence.get("day"),
        "habitat": occurrence.get("habitat"),
        "elevation": occurrence.get("elevation"),
        "basis_of_record": occurrence.get("basisOfRecord"),
        "dataset_key": occurrence.get("datasetKey"),
        "institution_code": occurrence.get("institutionCode"),
        "recorded_by": occurrence.get("recordedBy"),
        "identified_by": occurrence.get("identifiedBy"),
    }
    
    for occurrence in occurrences:
        try:
            country = occurrence.get("country", "Unknown")
            state = occurrence.get("stateProvince", "Unknown")
            habitat = occurrence.get("habitat", "Unknown")
            
            # Crear clave única para la zona
            zone_key = f"{country}|{state}|{habitat}"
            
            if zone_key not in zones_data:
                zones_data[zone_key] = {
                    "country": country,
                    "state_province": state,
                    "habitat": habitat,
                    "occurrences_count": 0,
                    "coordinates": []
                }
            
            zones_data[zone_key]["occurrences_count"] += 1
            
            # Guardar coordenadas para análisis posterior
            lat = occurrence.get("decimalLatitude")
            lon = occurrence.get("decimalLongitude")
            if lat and lon:
                zones_data[zone_key]["coordinates"].append({
                    "latitude": lat,
                    "longitude": lon
                })
                
        except Exception as e:
            print(f" Error procesando ocurrencia: {e}")
            continue
    
    print(f"✓ Se extrajeron {len(zones_data)} zonas ecológicas únicas")
    
    # Imprimir resumen
    for zone_key, zone_info in list(zones_data.items())[:5]:  # Mostrar primeras 5
        print(f"  - {zone_key}: {zone_info['occurrences_count']} ocurrencias")
    
    return zones_data
