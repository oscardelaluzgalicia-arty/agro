#!/usr/bin/env python3
"""
Script de debug para entender la estructura de respuesta de iNaturalist
"""
import requests
import json
from datetime import datetime

print("🔍 Analizando estructura de respuesta de iNaturalist...\n")

# Parámetros de búsqueda para México
params = {
    "q": "Solanum lycopersicum",
    "place_id": 6793,  # México
    "geo": True,  # Solo con observaciones georreferenciadas
    "per_page": 5,  # Solo 5 primeras
    "order_by": "id",
    "order": "desc"
}

try:
    print(f"📤 Request URL:")
    url = "https://api.inaturalist.org/v1/observations"
    print(f"   {url}")
    print(f"\n📋 Parameters:")
    for k, v in params.items():
        print(f"   {k}: {v}")
    
    print("\n⏳ Consultando iNaturalist API...")
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    total_results = data.get("total_results", 0)
    results = data.get("results", [])
    
    print(f"\n✅ Respuesta recibida")
    print(f"   Total de observaciones en iNaturalist (México): {total_results}")
    print(f"   Observaciones en esta respuesta: {len(results)}")
    
    if results:
        print(f"\n📌 Estructura de PRIMERA observación:")
        obs = results[0]
        print(f"\n{json.dumps(obs, indent=2, default=str)[:2000]}...")
        
        print(f"\n\n🔑 CAMPOS IMPORTANTES de la primera observación:")
        important_fields = [
            "id",
            "species_guess",
            "scientific_name",
            "latitude",
            "longitude",
            "place_guess",
            "observed_on",
            "created_at",
            "user",
            "quality_grade",
            "positional_accuracy",
            "license",
            "attribution"
        ]
        
        for field in important_fields:
            value = obs.get(field)
            if field == "user" and isinstance(value, dict):
                print(f"   {field}: {value.get('login')} (id: {value.get('id')})")
            else:
                print(f"   {field}: {value}")
        
        print(f"\n📊 Análisis de TODAS las observaciones ({len(results)}):")
        coords_count = sum(1 for r in results if r.get("latitude") and r.get("longitude"))
        place_guess_count = sum(1 for r in results if r.get("place_guess"))
        
        print(f"   ✓ Con coordenadas (lat/lon): {coords_count}/{len(results)}")
        print(f"   ✓ Con place_guess: {place_guess_count}/{len(results)}")
        
        print(f"\n🗺️  Coordenadas encontradas:")
        for i, r in enumerate(results, 1):
            lat = r.get("latitude")
            lon = r.get("longitude")
            place = r.get("place_guess")
            print(f"   [{i}] ({lat}, {lon}) - {place}")
    
    print(f"\n✨ Análisis completado")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error en la solicitud: {e}")
except Exception as e:
    print(f"❌ Error procesando respuesta: {e}")
