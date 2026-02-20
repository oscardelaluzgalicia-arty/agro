"""
Router para el traductor semantico - Resuelve nombres comunes a cientificos
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import auth_middleware
from traductorsemantico_ia.translator import get_translator
from traductorsemantico_ia.gbif_validator import get_validator


router = APIRouter()


class ResolveCommonNameRequest(BaseModel):
    """Modelo de request para resolver nombre comun"""
    name: str


class ScientificNameResult(BaseModel):
    """Modelo de resultado para un nombre cientifico validado"""
    inputName: str
    scientificName: str
    canonicalName: str
    taxonKey: int
    rank: str
    status: str
    confidence: int
    matchType: str
    phylum: str
    scientificNameAuthorship: str


class ResolveCommonNameResponse(BaseModel):
    """Modelo de respuesta del endpoint"""
    commonName: str
    scientificNames: list[ScientificNameResult]
    totalFound: int


@router.post("/resolve-common-name")
def resolve_common_name(
    body: ResolveCommonNameRequest,
    _=Depends(auth_middleware)
):
    """
    Resuelve un nombre comun a nombres cientificos validados con GBIF
    
    Flujo:
    1. Usuario => nombre comun (ej: "uva")
    2. IA => genera 3 nombres cientificos candidatos
    3. GBIF => valida y obtiene datos taxonomicos completos
    4. API => responde con datos normalizados
    
    Request body:
    {
        "name": "uva"
    }
    
    Returns:
        ResolveCommonNameResponse con los nombres cientificos validados
        
    Raises:
        HTTPException 400: Si el nombre esta vacio
        HTTPException 404: Si no se encontraron nombres validos en GBIF
        HTTPException 500: Si hay error en IA o GBIF
    """
    name = body.name
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="El nombre comun no puede estar vacio")
    
    name = name.strip().lower()
    
    try:
        # Paso 1: Llamar a IA para obtener nombres cientificos
        translator = get_translator()
        scientific_names = translator.translate_to_scientific_names(name)
        
        if not scientific_names:
            raise HTTPException(
                status_code=404,
                detail=f"IA no pudo identificar nombres cientificos para '{name}'"
            )
        
        # Paso 2: Validar con GBIF
        validator = get_validator()
        validated_results = validator.validate_multiple(scientific_names)
        
        if not validated_results:
            raise HTTPException(
                status_code=404,
                detail=f"No se pudo validar ningun nombre cientifico en GBIF para '{name}'"
            )
        
        # Paso 3: Transformar resultados al formato de respuesta (usar dicts para evitar errores de validacion)
        scientific_names_response = []
        for result in validated_results:
            gbif_data = result.get("gbifData", {})
            try:
                taxon_key = gbif_data.get("usageKey") or gbif_data.get("taxonKey")
                if taxon_key is not None:
                    try:
                        taxon_key = int(taxon_key)
                    except Exception:
                        taxon_key = None

                item = {
                    "inputName": result.get("inputName"),
                    "scientificName": gbif_data.get("scientificName"),
                    "canonicalName": gbif_data.get("canonicalName"),
                    "taxonKey": taxon_key,
                    "rank": gbif_data.get("rank"),
                    "status": gbif_data.get("status"),
                    "confidence": gbif_data.get("confidence"),
                    "matchType": gbif_data.get("matchType"),
                    "phylum": gbif_data.get("phylum"),
                    "scientificNameAuthorship": gbif_data.get("scientificNameAuthorship")
                }
                scientific_names_response.append(item)
            except Exception:
                # Ignorar resultados problematicos pero continuar
                continue

        # Paso 4: Retornar respuesta como dict
        return {
            "commonName": name,
            "scientificNames": scientific_names_response,
            "totalFound": len(scientific_names_response)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando solicitud: {str(e)}"
        )


@router.post("/resolve-common-name-batch")
def resolve_common_name_batch(
    body: dict,
    _=Depends(auth_middleware)
):
    """
    Resuelve multiples nombres comunes en una sola solicitud
    
    Request body:
    {
        "names": ["uva", "manzana", "tomate"]
    }
    
    Returns:
        Lista de ResolveCommonNameResponse
    """
    names = body.get("names", [])
    
    if not names or not isinstance(names, list):
        raise HTTPException(
            status_code=400,
            detail="Se requiere un array 'names' con nombres comunes"
        )
    
    results = []
    for name in names:
        try:
            # Reutilizar la logica del endpoint anterior
            request_body = ResolveCommonNameRequest(name=name)
            response = resolve_common_name(request_body)
            results.append({
                "status": "success",
                "data": response
            })
        except HTTPException as e:
            results.append({
                "status": "error",
                "name": name,
                "error": e.detail
            })
        except Exception as e:
            results.append({
                "status": "error",
                "name": name,
                "error": str(e)
            })
    
    return {
        "totalRequests": len(names),
        "successfulResolutions": len([r for r in results if r["status"] == "success"]),
        "results": results
    }
