"""
Muestreo inteligente por grid H3 o selección aleatoria estratificada
"""
import random
from typing import Dict, List, Tuple
from collections import defaultdict


class GridSampler:
    """
    Realiza muestreo estratificado de puntos para evitar sesgos geográficos
    """
    
    @staticmethod
    def get_grid_cell(lat: float, lon: float, resolution: int = 4) -> str:
        """
        Calcula hash de grid H3 para una coordenada
        Implementación simplificada: división en celdas rectangulares
        
        Args:
            lat: Latitud
            lon: Longitud
            resolution: Tamaño de celda aproximado en grados
            
        Returns:
            Identificador de celda de grid
        """
        cell_lat = int(lat / resolution) * resolution
        cell_lon = int(lon / resolution) * resolution
        return f"{cell_lat}_{cell_lon}"
    
    @staticmethod
    def stratified_random_sample(
        occurrences: List[Dict],
        sample_size: int = None,
        grid_resolution: int = 4
    ) -> List[Dict]:
        """
        Selecciona puntos estratificados aleatoriamente para evitar clustering
        
        Args:
            occurrences: Lista de ocurrencias con fields decimal_latitude, decimal_longitude
            sample_size: Número máximo de puntos a retornar. Si None, usa 20% de los datos
            grid_resolution: Tamaño de celda del grid en grados
            
        Returns:
            Lista de ocurrencias muestreadas
        """
        if not occurrences:
            return []
        
        # Setear sample_size por defecto
        if sample_size is None:
            sample_size = max(10, int(len(occurrences) * 0.2))
        
        # Agrupar por celda de grid
        grid_groups = defaultdict(list)
        for occ in occurrences:
            lat = occ.get("decimal_latitude")
            lon = occ.get("decimal_longitude")
            
            if lat is not None and lon is not None:
                cell = GridSampler.get_grid_cell(lat, lon, grid_resolution)
                grid_groups[cell].append(occ)
        
        # Seleccionar aleatoriamente de cada celda
        sampled = []
        cells = list(grid_groups.keys())
        
        if len(cells) >= sample_size:
            # Distribuir uniformemente entre celdas
            points_per_cell = max(1, sample_size // len(cells))
            
            for cell in cells:
                group = grid_groups[cell]
                n = min(points_per_cell, len(group))
                sampled.extend(random.sample(group, n))
                
                if len(sampled) >= sample_size:
                    break
        else:
            # Si hay pocos clusters, tomar todos
            for group in grid_groups.values():
                sampled.extend(group)
        
        return sampled[:sample_size]
    
    @staticmethod
    def filter_outliers(
        values: List[float],
        lower_percentile: int = 5,
        upper_percentile: int = 95
    ) -> List[float]:
        """
        Filtra valores extremos usando percentiles
        
        Args:
            values: Lista de valores
            lower_percentile: Percentil inferior
            upper_percentile: Percentil superior
            
        Returns:
            Lista de valores dentro del rango
        """
        if not values:
            return []
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        lower_idx = max(0, int((lower_percentile / 100) * n))
        upper_idx = min(n - 1, int((upper_percentile / 100) * n))
        
        lower_bound = sorted_vals[lower_idx]
        upper_bound = sorted_vals[upper_idx]
        
        return [v for v in values if lower_bound <= v <= upper_bound]
