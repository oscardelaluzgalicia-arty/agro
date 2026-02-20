"""
Módulo para validación de nombres científicos contra GBIF
"""
from typing import Optional, Dict, Any
import requests
from .config import GBIF_CONFIDENCE_THRESHOLD, GBIF_MATCH_ENDPOINT


class GBIFValidator:
    """Validador de nombres científicos usando GBIF API"""
    
    def __init__(self, confidence_threshold: int = GBIF_CONFIDENCE_THRESHOLD):
        """
        Inicializa el validador
        
        Args:
            confidence_threshold: Puntuación mínima de confianza (0-100)
        """
        self.confidence_threshold = confidence_threshold
        self.endpoint = GBIF_MATCH_ENDPOINT
    
    def validate(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """
        Valida un nombre científico contra GBIF
        
        Args:
            scientific_name: Nombre científico a validar
            
        Returns:
            Dict con datos de GBIF si es válido, None si no
        """
        try:
            params = {"name": scientific_name}
            response = requests.get(self.endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar confianza mínima
            if data.get("confidence", 0) >= self.confidence_threshold:
                return self._normalize_response(data)
            
            return None
            
        except requests.RequestException as e:
            print(f"Error validando con GBIF: {str(e)}")
            return None
    
    def _normalize_response(self, gbif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza la respuesta de GBIF
        
        Args:
            gbif_data: Datos crudos de GBIF
            
        Returns:
            Dict normalizado con campos principales
        """
        return {
            "scientificName": gbif_data.get("scientificName"),
            "canonicalName": gbif_data.get("canonicalName"),
            "usageKey": gbif_data.get("usageKey"),
            "taxonKey": gbif_data.get("taxonKey"),
            "rank": gbif_data.get("rank"),
            "status": gbif_data.get("status"),
            "confidence": gbif_data.get("confidence"),
            "matchType": gbif_data.get("matchType"),
            "phylum": gbif_data.get("phylum"),
            "scientificNameAuthorship": gbif_data.get("scientificNameAuthorship")
        }
    
    def validate_multiple(self, scientific_names: list) -> list:
        """
        Valida múltiples nombres científicos
        
        Args:
            scientific_names: Lista de nombres científicos
            
        Returns:
            Lista de nombres validados con sus datos GBIF
        """
        results = []
        for name in scientific_names:
            validated = self.validate(name)
            if validated:
                results.append({
                    "inputName": name,
                    "gbifData": validated
                })
        
        return results


def get_validator() -> GBIFValidator:
    """Factory function para obtener instancia del validador"""
    return GBIFValidator()
