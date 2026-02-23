"""
Módulo principal para calcular el nicho climático de una especie
Orquesta todo el pipeline desde ocurrencias hasta percentiles
"""
from typing import Dict, List
from app.crud import crud_action
from .open_meteo_client import OpenMeteoClient
from .open_elevation_client import OpenElevationClient
from .grid_sampling import GridSampler
from .percentile_calculator import PercentileCalculator


class ClimateNicheCalculator:
    """
    Pipeline completo para calcular nicho climático
    """
    
    @staticmethod
    def calculate(id_species: int, sample_size: int = None) -> Dict:
        """
        Ejecuta el pipeline completo:
        1. Obtener coordenadas de ocurrencias
        2. Muestreo inteligente
        3. Obtener clima histórico
        4. Obtener altitud
        5. Calcular percentiles
        
        Args:
            id_species: ID de la especie
            sample_size: Cantidad de puntos a muestrear (default: 20% o mínimo 10)
            
        Returns:
            Dict con todo el nicho climático calculado
        """
        # PASO 1: Obtener ocurrencias
        print(f"[1/5] Obteniendo ocurrencias para especie {id_species}")
        occurrences = ClimateNicheCalculator._get_occurrences(id_species)
        
        if not occurrences:
            return {
                "error": "No se encontraron ocurrencias para esta especie",
                "id_species": id_species
            }
        
        print(f"  → {len(occurrences)} ocurrencias encontradas")
        
        # PASO 2: Muestreo inteligente
        print(f"[2/5] Realizando muestreo estratificado")
        sampled = GridSampler.stratified_random_sample(
            occurrences,
            sample_size=sample_size,
            grid_resolution=5
        )
        print(f"  → {len(sampled)} puntos seleccionados después del muestreo")
        
        # PASO 3: Obtener clima histórico
        print(f"[3/5] Obteniendo datos climáticos de Open-Meteo")
        climate_list = []
        coords_for_elevation = []
        
        for i, occ in enumerate(sampled):
            lat = occ.get("decimal_latitude")
            lon = occ.get("decimal_longitude")
            
            if lat is None or lon is None:
                continue
            
            # Obtener clima
            daily_data = OpenMeteoClient.get_climate_data(lat, lon)
            annual_stats = OpenMeteoClient.calculate_annual_stats(daily_data)
            
            if annual_stats:
                climate_list.append(annual_stats)
                coords_for_elevation.append((lat, lon))
            
            if (i + 1) % 5 == 0:
                print(f"  → {i + 1}/{len(sampled)} puntos procesados")
        
        print(f"  → {len(climate_list)} puntos con datos climáticos válidos")
        
        if not climate_list:
            return {
                "error": "No se pudieron obtener datos climáticos para las ocurrencias",
                "id_species": id_species
            }
        
        # PASO 4: Obtener altitud
        print(f"[4/5] Obteniendo datos de altitud")
        elevation_list = []
        if coords_for_elevation:
            elevation_list = OpenElevationClient.get_elevations_batch(coords_for_elevation)
            print(f"  → {sum(1 for e in elevation_list if e is not None)} altitudes obtenidas")
        
        # PASO 5: Calcular percentiles
        print(f"[5/5] Calculando percentiles")
        
        # Extraer listas de datos
        temp_min_list, temp_max_list, rainfall_list = (
            OpenMeteoClient.extract_lists_for_percentiles(climate_list)
        )
        
        # Calcular percentiles
        niche_data = PercentileCalculator.calculate_climate_percentiles(
            temp_min_list,
            temp_max_list,
            rainfall_list,
            elevation_list
        )
        
        niche_data["id_species"] = id_species
        niche_data["points_sampled"] = len(sampled)
        niche_data["points_with_climate"] = len(climate_list)
        
        print(f"  ✓ Nicho climático calculado exitosamente")
        
        return niche_data
    
    @staticmethod
    def _get_occurrences(id_species: int) -> List[Dict]:
        """
        Obtiene ocurrencias de una especie usando CRUD genérico
        
        Args:
            id_species: ID de la especie
            
        Returns:
            Lista de ocurrencias con coordenadas
        """
        try:
            result = crud_action(
                action="read",
                table="occurrences",
                where={"id_species": id_species}
            )
            return result if result else []
        except Exception as e:
            print(f"Error fetching occurrences: {str(e)}")
            return []
