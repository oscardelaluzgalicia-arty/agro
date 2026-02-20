"""
Ejemplo de integración del Traductor Semántico con GBIF y la Base de Datos
Muestra cómo usar el sistema para enriquecer automáticamente la BD
"""

import requests
from typing import Optional, Dict, Any


class SemanticEnrichmentOrchestrator:
    """
    Orquestador que coordina:
    1. Traducción de nombre común → científico
    2. Validación con GBIF
    3. Importación de datos a la BD agronomic
    """
    
    def __init__(self, api_url: str, jwt_token: str):
        """
        Inicializa el orquestador
        
        Args:
            api_url: URL base de la API (ej: http://localhost:8000)
            jwt_token: Token JWT para autenticación
        """
        self.api_url = api_url.rstrip("/")
        self.jwt_token = jwt_token
        self.headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
    
    def enrich_from_common_name(self, common_name: str) -> Dict[str, Any]:
        """
        Pipeline completo: nombre común → especificación de especies en BD
        
        Flujo:
        1️⃣ Traducir nombre común a científicos
        2️⃣ Validar con GBIF
        3️⃣ Importar cada especie a la BD
        4️⃣ Enriquecer con datos agronómicos
        
        Args:
            common_name: Nombre común de la planta
            
        Returns:
            Dict con resultado del enriquecimiento
        """
        print(f"\n{'='*60}")
        print(f"🌱 ENRIQUECIMIENTO: {common_name.upper()}")
        print(f"{'='*60}")
        
        try:
            # 1️⃣ PASO 1: Traducir con IA
            print(f"\n1️⃣  Traduciendo '{common_name}' a nombres científicos...")
            response = requests.get(
                f"{self.api_url}/api/v1/semantic/resolve-common-name",
                params={"name": common_name},
                headers=self.headers
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "step": "semantic_translation",
                    "error": response.json().get("detail", "Error en traducción")
                }
            
            semantic_result = response.json()
            print(f"   ✅ Se encontraron {semantic_result['totalFound']} nombres científicos")
            
            # 2️⃣ PASO 2: Importar especies de GBIF
            print(f"\n2️⃣  Importando especies de GBIF...")
            imported_species = []
            
            for sci_name_obj in semantic_result["scientificNames"]:
                sci_name = sci_name_obj["scientificName"]
                print(f"   Importando: {sci_name}")
                
                import_response = requests.post(
                    f"{self.api_url}/api/v1/gbif/import",
                    json={
                        "name": sci_name,
                        "country": "MX"
                    },
                    headers=self.headers
                )
                
                if import_response.status_code == 200:
                    species_data = import_response.json()
                    imported_species.append({
                        "scientificName": sci_name,
                        "gbifData": sci_name_obj,
                        "speciesData": species_data
                    })
                    print(f"      ✅ Importado exitosamente")
                else:
                    print(f"      ❌ Error: {import_response.json()}")
            
            if not imported_species:
                return {
                    "status": "error",
                    "step": "gbif_import",
                    "error": "No se pudieron importar especies de GBIF"
                }
            
            # PASO 3: Enriquecer agronomicamente
            print(f"\nPaso 3: Enriqueciendo con datos agronomicos...")
            enriched_species = []
            
            for species in imported_species:
                # Obtener el id_species de los datos importados
                if "idEspecies" in species["speciesData"]:
                    species_id = species["speciesData"]["idEspecies"]
                else:
                    # Intentar acceder la respuesta de otra forma
                    print(f"      ADVERTENCIA - No se encontro ID de especie, saltando enriquecimiento agronomic")
                    continue
                
                print(f"   Enriqueciendo especie ID: {species_id}")
                
                enrich_response = requests.post(
                    f"{self.api_url}/api/v1/enrich/agronomy",
                    json={"id_species": species_id},
                    headers=self.headers
                )
                
                if enrich_response.status_code == 200:
                    agro_data = enrich_response.json()
                    species["agronomicData"] = agro_data
                    enriched_species.append(species)
                    print(f"      OK - Enriquecimiento completo")
                else:
                    print(f"      ADVERTENCIA - Error en enriquecimiento: {enrich_response.json()}")
                    enriched_species.append(species)  # Agregar igual sin datos agro
            
            return {
                "status": "success",
                "commonName": common_name,
                "totalSpecies": len(enriched_species),
                "species": enriched_species
            }
            
        except requests.RequestException as e:
            return {
                "status": "error",
                "error": f"Error de conexión: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error inesperado: {str(e)}"
            }
    
    def enrich_batch(self, common_names: list) -> Dict[str, Any]:
        """
        Enriquece múltiples nombres comunes
        
        Args:
            common_names: Lista de nombres comunes
            
        Returns:
            Dict con resultados de todos los enriquecimientos
        """
        results = []
        
        for common_name in common_names:
            result = self.enrich_from_common_name(common_name)
            results.append(result)
        
        return {
            "totalRequests": len(common_names),
            "successfulEnrichments": len([r for r in results if r.get("status") == "success"]),
            "results": results
        }
    
    def print_summary(self, enrichment_result: Dict[str, Any]) -> None:
        """
        Imprime un resumen legible del resultado del enriquecimiento
        
        Args:
            enrichment_result: Resultado de enrich_from_common_name()
        """
        if enrichment_result.get("status") == "error":
            print(f"\nERROR - Error: {enrichment_result.get('error')}")
            return
        
        print(f"\n{'='*60}")
        print(f"RESUMEN DE ENRIQUECIMIENTO")
        print(f"{'='*60}")
        print(f"Nombre comun: {enrichment_result.get('commonName')}")
        print(f"Especies procesadas: {enrichment_result.get('totalSpecies')}")
        
        for i, species in enumerate(enrichment_result.get("species", []), 1):
            print(f"\n{i}. {species['scientificName']}")
            gbif = species["gbifData"]
            print(f"   Confianza GBIF: {gbif['confidence']}%")
            print(f"   Rango: {gbif['rank']}")
            print(f"   TaxonKey: {gbif['taxonKey']}")
            if "agronomicData" in species:
                ops = species["agronomicData"].get("operations", {})
                print(f"   Enriquecimientos: {', '.join(ops.keys())}")


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    API_URL = "http://localhost:8000"
    JWT_TOKEN = "your_jwt_token_here"
    
    # Crear orquestador
    orchestrator = SemanticEnrichmentOrchestrator(API_URL, JWT_TOKEN)
    
    # Ejemplo 1: Enriquecer un nombre comun
    print("\nEJEMPLO 1: Enriquecer un nombre comun")
    print("-" * 60)
    
    result = orchestrator.enrich_from_common_name("uva")
    orchestrator.print_summary(result)
    
    # Ejemplo 2: Enriquecer multiples nombres
    print("\n\nEJEMPLO 2: Enriquecer multiples nombres")
    print("-" * 60)
    
    batch_result = orchestrator.enrich_batch(["manzana", "tomate", "lechuga"])
    
    print(f"\n{'='*60}")
    print("RESUMEN DE LOTE")
    print(f"{'='*60}")
    print(f"Total de solicitudes: {batch_result['totalRequests']}")
    print(f"Enriquecimientos exitosos: {batch_result['successfulEnrichments']}")
    
    for result in batch_result['results']:
        if result['status'] == 'success':
            print(f"\nOK - {result['commonName']}: {result['totalSpecies']} especies")
        else:
            print(f"\nERROR - {result.get('commonName', 'desconocido')}: {result['error']}")
