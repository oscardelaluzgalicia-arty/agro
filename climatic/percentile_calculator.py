"""
Cálculo de percentiles para definir rangos climáticos
"""
from typing import List, Dict


class PercentileCalculator:
    """
    Calcula percentiles 5, 25, 75, 95 de listas de datos climáticos
    """
    
    @staticmethod
    def percentile(data: List[float], p: int) -> float:
        """
        Calcula el percentil p de una lista de datos
        
        Args:
            data: Lista de valores
            p: Percentil (0-100)
            
        Returns:
            Valor del percentil
        """
        if not data:
            return None
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        if p == 0:
            return sorted_data[0]
        if p == 100:
            return sorted_data[-1]
        
        # Interpolación lineal
        rank = (p / 100) * (n - 1)
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, n - 1)
        
        if lower_idx == upper_idx:
            return sorted_data[lower_idx]
        
        # Interpolar entre dos valores
        fraction = rank - lower_idx
        return (sorted_data[lower_idx] * (1 - fraction) + 
                sorted_data[upper_idx] * fraction)
    
    @staticmethod
    def calculate_climate_percentiles(
        temp_min_list: List[float],
        temp_max_list: List[float],
        rainfall_list: List[float],
        altitude_list: List[float] = None
    ) -> Dict:
        """
        Calcula todos los percentiles necesarios para climate_requirements
        
        Args:
            temp_min_list: Lista de temperaturas mínimas
            temp_max_list: Lista de temperaturas máximas
            rainfall_list: Lista de precipitaciones
            altitude_list: Lista de altitudes (opcional)
            
        Returns:
            Dict con todos los percentiles calculados
        """
        result = {
            # Temperatura
            "temp_min": PercentileCalculator.percentile(temp_min_list, 5),
            "temp_opt_min": PercentileCalculator.percentile(temp_min_list, 25),
            "temp_opt_max": PercentileCalculator.percentile(temp_max_list, 75),
            "temp_max": PercentileCalculator.percentile(temp_max_list, 95),
            
            # Precipitación
            "rainfall_min": PercentileCalculator.percentile(rainfall_list, 5),
            "rainfall_opt_min": PercentileCalculator.percentile(rainfall_list, 25),
            "rainfall_opt_max": PercentileCalculator.percentile(rainfall_list, 75),
            "rainfall_max": PercentileCalculator.percentile(rainfall_list, 95),
        }
        
        # Altitud (si disponible)
        if altitude_list and any(a is not None for a in altitude_list):
            altitude_list = [a for a in altitude_list if a is not None]
            result["altitude_min"] = PercentileCalculator.percentile(altitude_list, 5)
            result["altitude_max"] = PercentileCalculator.percentile(altitude_list, 95)
        
        # Redondear a 2 decimales
        return {k: round(v, 2) if v is not None else None 
                for k, v in result.items()}
