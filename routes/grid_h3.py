from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import auth_middleware
import h3

router = APIRouter()


class GridRequest(BaseModel):
    state: str | None = None
    resolution: int = 5


# Default bounding box for Mexico (approx)
STATE_BBOX = {
    "mexico": {  # Estado de México
        "min_lat": 18.5,
        "max_lat": 20.3,
        "min_lon": -100.5,
        "max_lon": -98.5
    },
    "jalisco": {
        "min_lat": 18.9,
        "max_lat": 22.8,
        "min_lon": -105.7,
        "max_lon": -101.2
    }
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