# App + endpoint único
from fastapi import FastAPI, Depends, Request, BackgroundTasks
from .auth import login, auth_middleware
from .crud import crud_action
from .db import get_connection
from routes.gbif import router as gbif_router
from routes.semantic_translator import router as semantic_translator_router
from agronomic.agronomic import enrich_species_agronomy_sync

app = FastAPI()

@app.get("/")
def health():
    return {
        "db_connected": bool(get_connection())
    }

@app.post("/login")
def login_endpoint(body: dict):
    return {
        "token": login(body["username"], body["password"])
    }

@app.post("/api/v1/crud")
async def crud_endpoint(
    body: dict,
    request: Request,
    _=Depends(auth_middleware)
):
    return crud_action(
        action=body["action"],
        table=body["table"],
        data=body.get("data"),
        where=body.get("where")
    )

@app.post("/api/v1/enrich/agronomy")
def enrich_agronomy_endpoint(
    body: dict,
    request: Request,
    _=Depends(auth_middleware)
):
    """
    Ejecuta el pipeline paralelo de enriquecimiento agronómico para una especie
    
    Request body:
    {
        "id_species": int
    }
    
    Response:
    {
        "id_species": int,
        "species_name": str,
        "timestamp": str,
        "operations": {
            "climate": {...},
            "crop_profile": {...},
            "soil": {...},
            "calendar": {...},
            "companions": {...}
        }
    }
    """
    id_species = body.get("id_species")
    if not id_species:
        return {"error": "Missing id_species in request body"}
    
    db = get_connection()
    if not db:
        return {"error": "Database connection failed"}
    
    try:
        result = enrich_species_agronomy_sync(id_species, db)
        return result
    finally:
        db.close()

app.include_router(
    gbif_router,
    prefix="/api/v1/gbif",
    tags=["GBIF"]
)

app.include_router(
    semantic_translator_router,
    prefix="/api/v1/semantic",
    tags=["Semantic Translator"]
)