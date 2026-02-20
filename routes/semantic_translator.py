"""
Router para el traductor semántico - Resuelve nombres comunes a científicos
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import auth_middleware
from traductorsemantico_ia.translator import get_translator
from traductorsemantico_ia.gbif_validator import get_validator


router = APIRouter()


class ResolveCommonNameRequest(BaseModel):
    """Modelo de request para resolver nombre común"""
    name: str


class ScientificNameResult(BaseModel):
    """Modelo de resultado para un nombre científico validado"""
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


@router.get("/resolve-common-name")
def resolve_common_name(
    name: str,
    _=Depends(auth_middleware)
):
    """
    Resuelve un nombre común a nombres científicos validados con GBIF
    
    Flujo:
    1. Usuario => nombre comun (ej: "uva")
    2. IA => genera 3 nombres cientificos candidatos
    3. GBIF => valida y obtiene datos taxonomicos completos
    4. API => responde con datos normalizados
    
    Args:
        name: Nombre común de la planta/fruta/verdura
        
    Returns:
        ResolveCommonNameResponse con los nombres científicos validados
        
    Raises:
        HTTPException 400: Si el nombre está vacío
        HTTPException 404: Si no se encontraron nombres válidos en GBIF
        HTTPException 500: Si hay error en IA o GBIF
    """
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="El nombre común no puede estar vacío")
    
    name = name.strip().lower()
    
    try:
        # Paso 1: Llamar a IA para obtener nombres cientificos
        translator = get_translator()
        scientific_names = translator.translate_to_scientific_names(name)
        
        if not scientific_names:
            raise HTTPException(
                status_code=404,
                detail=f"IA no pudo identificar nombres científicos para '{name}'"
            )
        
        # Paso 2: Validar con GBIF
        validator = get_validator()
        validated_results = validator.validate_multiple(scientific_names)
        
        if not validated_results:
            raise HTTPException(
                status_code=404,
                detail=f"No se pudo validar ningún nombre científico en GBIF para '{name}'"
            )
        
        # Paso 3: Transformar resultados al formato de respuesta
        scientific_names_response = []
        for result in validated_results:
            gbif_data = result["gbifData"]
            scientific_names_response.append(
                ScientificNameResult(
                    inputName=result["inputName"],
                    scientificName=gbif_data["scientificName"],
                    canonicalName=gbif_data["canonicalName"],
                    taxonKey=gbif_data["usageKey"],
                    rank=gbif_data["rank"],
                    status=gbif_data["status"],
                    confidence=gbif_data["confidence"],
                    matchType=gbif_data["matchType"],
                    phylum=gbif_data["phylum"],
                    scientificNameAuthorship=gbif_data["scientificNameAuthorship"]
                )
            )
        
        # Paso 4: Retornar respuesta
        return ResolveCommonNameResponse(
            commonName=name,
            scientificNames=scientific_names_response,
            totalFound=len(scientific_names_response)
        )
        
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
    Resuelve múltiples nombres comunes en una sola solicitud
    
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
            # Reutilizar la lógica del endpoint anterior
            response = resolve_common_name(name)
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
