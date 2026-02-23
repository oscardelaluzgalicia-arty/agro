#!/bin/bash
# Script de ejemplos CURL para probar los endpoints de nicho climático
# Asegúrate de:
# 1. El servidor corriendo: python -m uvicorn app.main:app --reload
# 2. Reemplazar YOUR_TOKEN con un token válido (obtener en /login)

API_URL="http://localhost:8000/api/v1"
TOKEN="YOUR_TOKEN"

echo "=== Ejemplos de CURL para Nicho Climático ==="
echo ""

# ============================================
# 1. OPCIÓN RECOMENDADA: Calcular y guardar TODO
# ============================================
echo "1️⃣  CALCULAR Y GUARDAR (Recomendado)"
echo "---"
curl -X POST $API_URL/climatic/calculate-and-save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id_species": 3,
    "sample_size": 30,
    "frost_tolerance": "high",
    "drought_tolerance": "low"
  }' | jq .

echo ""
echo ""

# ============================================
# 2. Solo CALCULAR (sin guardar)
# ============================================
echo "2️⃣  SOLO CALCULAR (Preview)"
echo "---"
curl -X POST $API_URL/climatic/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id_species": 3,
    "sample_size": 25
  }' | jq .

echo ""
echo ""

# ============================================
# 3. GUARDAR dados pre-calculados
# ============================================
echo "3️⃣  GUARDAR DATOS PRE-CALCULADOS"
echo "---"
curl -X POST $API_URL/climatic/save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id_species": 2,
    "temp_min": 10.5,
    "temp_opt_min": 18.2,
    "temp_opt_max": 28.3,
    "temp_max": 35.1,
    "rainfall_min": 400,
    "rainfall_opt_min": 750,
    "rainfall_opt_max": 1200,
    "rainfall_max": 1800,
    "altitude_min": 0,
    "altitude_max": 2200,
    "frost_tolerance": "moderate",
    "drought_tolerance": "moderate"
  }' | jq .

echo ""
echo ""

# ============================================
# PRUEBAS CON DIFERENTES ESPECIES
# ============================================

echo "4️⃣  PRUEBA CON MAÍZ (id_species=1)"
echo "---"
curl -X POST $API_URL/climatic/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"id_species": 1}' | jq .

echo ""
echo ""

echo "5️⃣  PRUEBA CON ARROZ (id_species=2)"
echo "---"
curl -X POST $API_URL/climatic/calculate-and-save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id_species": 2,
    "sample_size": 20
  }' | jq .

echo ""
echo ""

# ============================================
# OBTENER DATOS GUARDADOS (CRUD genérico)
# ============================================

echo "6️⃣  LEER DATOS GUARDADOS (CRUD genérico)"
echo "---"
curl -X POST $API_URL/crud \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "action": "read",
    "table": "climate_requirements",
    "where": {"id_species": 3}
  }' | jq .

echo ""
echo ""

# ============================================
# NOTAS
# ============================================

cat << 'EOF'

📝 NOTAS IMPORTANTES:

1. OBTENER TOKEN:
   curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'

2. SAMPLE_SIZE:
   - Omitir = auto (20% de ocurrencias, mínimo 10)
   - Ejemplo: "sample_size": 50

3. RESPUESTA EXITOSA:
   - Status: 200 OK
   - Campo "success": true
   - Campo "operation": "created" o "updated"

4. CAMPOS OPCIONALES:
   - frost_tolerance: "high", "moderate", "low"
   - drought_tolerance: "high", "moderate", "low"

5. ERRORES COMUNES:
   - {"error": "No se encontraron ocurrencias..."}
     → La especie no tiene datos en BD
   
   - {"error": "No se pudieron obtener datos climáticos..."}
     → Open-Meteo no disponible o coordenadas inválidas
   
   - Missing id_species
     → Falta el campo requerido

6. TIEMPO DE EJECUCIÓN:
   - Pocas ocurrencias: 30-60 segundos
   - Muchas ocurrencias: 2-5 minutos

7. VERIFICAR PROGRESO:
   El endpoint imprime en console:
   [1/5] Obteniendo ocurrencias...
   [2/5] Realizando muestreo...
   [3/5] Obteniendo datos climáticos...
   [4/5] Obteniendo datos de altitud...
   [5/5] Calculando percentiles...

EOF
