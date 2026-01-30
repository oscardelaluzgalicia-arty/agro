#!/usr/bin/env python3
"""
Test script para probar la importación de especies con zonas ecológicas
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

# Test data - Usar nombre científico
species_name = sys.argv[1] if len(sys.argv) > 1 else "Solanum lycopersicum"

test_data = {
    "name": species_name,
    "country": "Mexico"
}

print(f"🧪 Testeando importación de: {test_data['name']}")
print(f"📤 POST {BASE_URL}/api/v1/gbif/import")
print(f"📋 Payload: {json.dumps(test_data, indent=2)}\n")
print("⏳ Esperando respuesta (esto puede tardar 1-2 minutos si hay muchas ocurrencias)...\n")

try:
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/gbif/import",
        json=test_data,
        timeout=300  # 5 minutos de timeout
    )
    elapsed = time.time() - start
    
    print(f"✅ Response Status: {response.status_code} (en {elapsed:.1f}s)\n")
    
    if response.status_code == 200:
        result = response.json()
        print("📊 RESULTADO:")
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"❌ Timeout después de 5 minutos - el servidor tardó demasiado")
except requests.exceptions.ConnectionError:
    print(f"❌ No se pudo conectar al servidor en {BASE_URL}")
    print("💡 Asegúrate de que uvicorn esté ejecutándose en otra terminal")
except Exception as e:
    print(f"❌ Error: {e}")


