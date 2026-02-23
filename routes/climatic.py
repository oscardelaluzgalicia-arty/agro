"""
Endpoints para cálculo de nicho climático
"""
from fastapi import APIRouter, Depends, Request
from app.auth import auth_middleware
from app.db import get_connection
from app.crud import crud_action
from climatic.climate_niche import ClimateNicheCalculator

router = APIRouter()


@router.post("/calculate")
def calculate_climate_niche(
    body: dict,
    request: Request,
    _=Depends(auth_middleware)
):
    """
    Calcula el nicho climático para una especie
    
    Request body:
    {
        "id_species": int,
        "sample_size": int (opcional, default: 20% de ocurrencias)
    }
    
    Response:
    {
        "id_species": int,
        "temp_min": float (5° percentil temp mínima),
        "temp_opt_min": float (25° percentil temp mínima),
        "temp_opt_max": float (75° percentil temp máxima),
        "temp_max": float (95° percentil temp máxima),
        "rainfall_min": float (5° percentil),
        "rainfall_opt_min": float (25° percentil),
        "rainfall_opt_max": float (75° percentil),
        "rainfall_max": float (95° percentil),
        "altitude_min": float (5° percentil),
        "altitude_max": float (95° percentil),
        "points_sampled": int,
        "points_with_climate": int
    }
    """
    id_species = body.get("id_species")
    sample_size = body.get("sample_size")
    
    if not id_species:
        return {"error": "Missing id_species in request body"}
    
    try:
        # Calcular nicho climático
        niche_data = ClimateNicheCalculator.calculate(
            id_species=id_species,
            sample_size=sample_size
        )
        
        if "error" in niche_data:
            return niche_data
        
        return niche_data
        
    except Exception as e:
        return {
            "error": str(e),
            "id_species": id_species
        }


@router.post("/save")
def save_climate_niche(
    body: dict,
    request: Request,
    _=Depends(auth_middleware)
):
    """
    Guarda el nicho climático calculado en climate_requirements
    
    Request body:
    {
        "id_species": int,
        "temp_min": float,
        "temp_opt_min": float,
        "temp_opt_max": float,
        "temp_max": float,
        "rainfall_min": float,
        "rainfall_opt_min": float,
        "rainfall_opt_max": float,
        "rainfall_max": float,
        "altitude_min": float,
        "altitude_max": float,
        "frost_tolerance": str (opcional),
        "drought_tolerance": str (opcional)
    }
    """
    id_species = body.get("id_species")
    
    if not id_species:
        return {"error": "Missing id_species in request body"}
    
    try:
        # Preparar datos para insertar/actualizar
        niche_data = {
            "id_species": id_species,
            "temp_min": body.get("temp_min"),
            "temp_opt_min": body.get("temp_opt_min"),
            "temp_opt_max": body.get("temp_opt_max"),
            "temp_max": body.get("temp_max"),
            "rainfall_min": body.get("rainfall_min"),
            "rainfall_opt_min": body.get("rainfall_opt_min"),
            "rainfall_opt_max": body.get("rainfall_opt_max"),
            "rainfall_max": body.get("rainfall_max"),
            "altitude_min": body.get("altitude_min"),
            "altitude_max": body.get("altitude_max"),
        }
        
        # Agregar campos opcionales si están presentes
        if "frost_tolerance" in body:
            niche_data["frost_tolerance"] = body["frost_tolerance"]
        if "drought_tolerance" in body:
            niche_data["drought_tolerance"] = body["drought_tolerance"]
        
        # Verificar si ya existe
        existing = crud_action(
            action="read",
            table="climate_requirements",
            where={"id_species": id_species}
        )
        
        if existing and len(existing) > 0:
            # Actualizar
            crud_action(
                action="update",
                table="climate_requirements",
                data=niche_data,
                where={"id_species": id_species}
            )
            operation = "updated"
        else:
            # Insertar
            crud_action(
                action="create",
                table="climate_requirements",
                data=niche_data
            )
            operation = "created"
        
        return {
            "success": True,
            "id_species": id_species,
            "operation": operation,
            "data": niche_data
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "id_species": id_species
        }


@router.post("/calculate-and-save")
def calculate_and_save_climate_niche(
    body: dict,
    request: Request,
    _=Depends(auth_middleware)
):
    """
    Calcula Y guarda el nicho climático en una sola operación
    
    Request body:
    {
        "id_species": int,
        "sample_size": int (opcional),
        "frost_tolerance": str (opcional),
        "drought_tolerance": str (opcional)
    }
    """
    id_species = body.get("id_species")
    sample_size = body.get("sample_size")
    
    if not id_species:
        return {"error": "Missing id_species in request body"}
    
    try:
        # Paso 1: Calcular
        print(f"\n=== Calculando nicho climático para especie {id_species} ===")
        niche_data = ClimateNicheCalculator.calculate(
            id_species=id_species,
            sample_size=sample_size
        )
        
        if "error" in niche_data:
            return niche_data
        
        # Paso 2: Guardar
        print(f"\n=== Guardando en BD ===")
        save_data = {
            "id_species": id_species,
            "temp_min": niche_data.get("temp_min"),
            "temp_opt_min": niche_data.get("temp_opt_min"),
            "temp_opt_max": niche_data.get("temp_opt_max"),
            "temp_max": niche_data.get("temp_max"),
            "rainfall_min": niche_data.get("rainfall_min"),
            "rainfall_opt_min": niche_data.get("rainfall_opt_min"),
            "rainfall_opt_max": niche_data.get("rainfall_opt_max"),
            "rainfall_max": niche_data.get("rainfall_max"),
            "altitude_min": niche_data.get("altitude_min"),
            "altitude_max": niche_data.get("altitude_max"),
        }
        
        # Agregar campos opcionales
        if body.get("frost_tolerance"):
            save_data["frost_tolerance"] = body["frost_tolerance"]
        if body.get("drought_tolerance"):
            save_data["drought_tolerance"] = body["drought_tolerance"]
        
        # Verificar si existe
        existing = crud_action(
            action="read",
            table="climate_requirements",
            where={"id_species": id_species}
        )
        
        if existing and len(existing) > 0:
            crud_action(
                action="update",
                table="climate_requirements",
                data=save_data,
                where={"id_species": id_species}
            )
            operation = "updated"
        else:
            crud_action(
                action="create",
                table="climate_requirements",
                data=save_data
            )
            operation = "created"
        
        return {
            "success": True,
            "id_species": id_species,
            "operation": operation,
            "niche_data": niche_data,
            "saved_data": save_data
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "id_species": id_species
        }
