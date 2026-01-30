# App + endpoint único
from fastapi import FastAPI, Depends, Request
from .auth import login, auth_middleware
from .crud import crud_action
from .db import get_connection
from routes.gbif import router as gbif_router

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
app.include_router(
    gbif_router,
    prefix="/api/v1/gbif",
    tags=["GBIF"]
)