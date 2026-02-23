"""
Cliente para obtener datos de altitud desde Open-Elevation API
"""
import requests
from typing import List, Dict


class OpenElevationClient:
    BASE_URL = "https://api.open-elevation.com/api/v1/lookup"
    
    @staticmethod
    def get_elevation(latitude: float, longitude: float) -> float:
        """
        Obtiene la altitud para una coordenada específica
        
        Args:
            latitude: Coordenada de latitud
            longitude: Coordenada de longitud
            
        Returns:
            Altitud en metros, o None si falla
        """
        params = {
            "locations": f"{latitude},{longitude}"
        }
        
        try:
            response = requests.get(OpenElevationClient.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                return data["results"][0]["elevation"]
            return None
        except Exception as e:
            print(f"Error fetching elevation for ({latitude}, {longitude}): {str(e)}")
            return None
    
    @staticmethod
    def get_elevations_batch(coords: List[tuple]) -> List[float]:
        """
        Obtiene altitudes para múltiples coordenadas
        
        Args:
            coords: Lista de tuplas (latitud, longitud)
            
        Returns:
            Lista de altitudes
        """
        elevations = []
        
        # Open-Elevation permite hasta ~100 ubicaciones por request
        batch_size = 100
        for i in range(0, len(coords), batch_size):
            batch = coords[i:i + batch_size]
            locations_str = "|".join([f"{lat},{lon}" for lat, lon in batch])
            
            params = {
                "locations": locations_str
            }
            
            try:
                response = requests.get(
                    OpenElevationClient.BASE_URL,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("results"):
                    elevations.extend([r["elevation"] for r in data["results"]])
            except Exception as e:
                print(f"Error fetching batch elevations: {str(e)}")
                # Continuar con otras ubicaciones
                elevations.extend([None] * len(batch))
        
        return elevations
