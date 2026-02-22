from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import auth_middleware
import h3

router = APIRouter()


class GridRequest(BaseModel):
    state: str | None = None
    resolution: int = 5


STATE_FILES = {
    "ags": "01-Ags.geojson",
    "bc": "02-Bc.geojson",
    "bcs": "03-Bcs.geojson",
    "camp": "04-Camp.geojson",
    "coah": "05-Coah.geojson",
    "col": "06-Col.geojson",
    "chis": "07-Chis.geojson",
    "chih": "08-Chih.geojson",
    "cdmx": "09-Cdmx.geojson",
    "dgo": "10-Dgo.geojson",
    "gto": "11-Gto.geojson",
    "gro": "12-Gro.geojson",
    "hgo": "13-Hgo.geojson",
    "jal": "14-Jal.geojson",
    "mex": "15-Mex.geojson",
    "mich": "16-Mich.geojson",
    "mor": "17-Mor.geojson",
    "nay": "18-Nay.geojson",
    "nl": "19-NL.geojson",
    "oax": "20-Oax.geojson",
    "pue": "21-Pue.geojson",
    "qro": "22-Qro.geojson",
    "qroo": "23-Qroo.geojson",
    "slp": "24-SLP.geojson",
    "sin": "25-Sin.geojson",
    "son": "26-Son.geojson",
    "tab": "27-Tab.geojson",
    "tmps": "28-Tmps.geojson",
    "tlax": "29-Tlax.geojson",
    "ver": "30-Ver.geojson",
    "yuc": "31-Yuc.geojson",
    "zac": "32-Zac.geojson",
}

@router.post("/grid-h3")
def create_h3_grid(body: GridRequest, _=Depends(auth_middleware)):

    if not body.state:
        raise HTTPException(status_code=400, detail="State is required")

    state_key = body.state.lower()

    if state_key not in STATE_BBOX:
        raise HTTPException(status_code=404, detail="State not supported")

    bbox = STATE_BBOX[state_key]
    resolution = body.resolution or 5

    # Crear polígono tipo GeoJSON (lon, lat)
    polygon = {
        "type": "Polygon",
        "coordinates": [[
            [bbox["min_lon"], bbox["min_lat"]],
            [bbox["max_lon"], bbox["min_lat"]],
            [bbox["max_lon"], bbox["max_lat"]],
            [bbox["min_lon"], bbox["max_lat"]],
            [bbox["min_lon"], bbox["min_lat"]],
        ]]
    }

    indexes = h3.polyfill(polygon, resolution, geo_json_conformant=True)

    features = []

    for idx in indexes:
        boundary = h3.h3_to_geo_boundary(idx, geo_json=True)
        polygon_coords = [[p[1], p[0]] for p in boundary]
        center_lat, center_lon = h3.h3_to_geo(idx)

        features.append({
            "h3": idx,
            "center": [center_lon, center_lat],
            "polygon": polygon_coords
        })

    return {
        "state": body.state,
        "resolution": resolution,
        "count": len(features),
        "hexagons": features
    }