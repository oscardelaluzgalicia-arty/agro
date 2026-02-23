"""
Cliente para obtener datos climáticos históricos de Open-Meteo
"""
import requests
from typing import Dict, List, Tuple
import statistics
from datetime import datetime, timedelta


class OpenMeteoClient:
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    @staticmethod
    def get_climate_data(
        latitude: float,
        longitude: float,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        Obtiene datos climáticos históricos para una ubicación
        
        Args:
            latitude: Coordenada de latitud
            longitude: Coordenada de longitud
            start_date: Fecha inicial (YYYY-MM-DD), por defecto 10 años atrás
            end_date: Fecha final (YYYY-MM-DD), por defecto hoy
            
        Returns:
            Dict con temperature_2m_min, temperature_2m_max, precipitation_sum
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum",
            "timezone": "UTC"
        }
        
        try:
            response = requests.get(OpenMeteoClient.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching climate data for ({latitude}, {longitude}): {str(e)}")
            return None
    
    @staticmethod
    def calculate_annual_stats(daily_data: Dict) -> Dict:
        """
        Calcula promedios anuales a partir de datos diarios
        
        Args:
            daily_data: Datos diarios desde Open-Meteo
            
        Returns:
            Dict con temp_media_anual, precipitacion_anual_total
        """
        if not daily_data or "daily" not in daily_data:
            return None
        
        daily = daily_data["daily"]
        temp_min = daily.get("temperature_2m_min", [])
        temp_max = daily.get("temperature_2m_max", [])
        precipitation = daily.get("precipitation_sum", [])
        
        if not (temp_min and temp_max and precipitation):
            return None
        
        # Calcular promedios anuales
        temp_media = (statistics.mean(temp_min) + statistics.mean(temp_max)) / 2
        precip_total = sum(precipitation)
        
        return {
            "temp_media_anual": round(temp_media, 2),
            "precipitacion_anual_total": round(precip_total, 2),
            "temp_min_daily": temp_min,
            "temp_max_daily": temp_max,
            "precipitation_daily": precipitation
        }
    
    @staticmethod
    def extract_lists_for_percentiles(
        climate_data_list: List[Dict]
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Extrae listas de temperaturas y precipitación de múltiples puntos
        
        Args:
            climate_data_list: Lista de resultados de calculate_annual_stats
            
        Returns:
            Tupla (lista_temp_min, lista_temp_max, lista_lluvia)
        """
        lista_temp_min = []
        lista_temp_max = []
        lista_lluvia = []
        
        for data in climate_data_list:
            if data is None:
                continue
            
            # Extraer valores extremos o promedios según corresponda
            daily_min = data.get("temp_min_daily", [])
            daily_max = data.get("temp_max_daily", [])
            daily_precip = data.get("precipitation_daily", [])
            
            if daily_min:
                lista_temp_min.extend(daily_min)
            if daily_max:
                lista_temp_max.extend(daily_max)
            if daily_precip:
                lista_lluvia.extend(daily_precip)
        
        return lista_temp_min, lista_temp_max, lista_lluvia
