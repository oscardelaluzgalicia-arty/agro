# 🌍 Climatic Niche Calculator

Módulo para calcular automáticamente el **nicho climático** de especies agrícolas/botánicas basándose en datos de ocurrencias reales.

## ✨ Características Principales

✅ **Muestreo inteligente** - Evita sesgos geográficos agrupando por grid  
✅ **Datos históricos** - 10+ años de clima desde Open-Meteo  
✅ **Percentiles automáticos** - Calcula 5%, 25%, 75%, 95%  
✅ **Altitud incluida** - Integración con Open-Elevation  
✅ **Sin API Keys** - APIs públicas completamente gratuitas  
✅ **Tolerancias opcionales** - Frost & drought tolerance annotations  
✅ **Almacenamiento automático** - Guarda en tabla `climate_requirements`  

---

## 📦 Módulos

### `climate_niche.py` - Orquestador Principal
Ejecuta todo el pipeline de 5 pasos:
1. Obtiene coordenadas de ocurrencias
2. Muestreo estratificado por grid
3. Consulta clima histórico (Open-Meteo)
4. Obtiene altitudes (Open-Elevation)
5. Calcula percentiles

```python
from climatic.climate_niche import ClimateNicheCalculator

result = ClimateNicheCalculator.calculate(
    id_species=3,
    sample_size=50
)
```

### `open_meteo_client.py` - Datos Climáticos
Consulta el archivo histórico de Open-Meteo:
- Temperatura mínima/máxima diaria
- Precipitación diaria
- Período: últimos 10 años (configurable)

```python
from climatic.open_meteo_client import OpenMeteoClient

data = OpenMeteoClient.get_climate_data(lat=36.5, lon=-5.7)
stats = OpenMeteoClient.calculate_annual_stats(data)
```

### `open_elevation_client.py` - Datos de Altitud
Obtiene elevación desde Open-Elevation:
- Soporta consultas de múltiples puntos (hasta 100 por request)
- Usa datos públicos de DEM

```python
from climatic.open_elevation_client import OpenElevationClient

elevation = OpenElevationClient.get_elevation(lat=36.5, lon=-5.7)
elevations = OpenElevationClient.get_elevations_batch(coords)
```

### `grid_sampling.py` - Muestreo Estratificado
Implementa muestreo por grid para evitar clustering:
- Divide mundo en celdas 5° × 5°
- Selecciona aleatoriamente de cada celda
- Garantiza cobertura geográfica

```python
from climatic.grid_sampling import GridSampler

sampled = GridSampler.stratified_random_sample(
    occurrences=occurrences,
    sample_size=50,
    grid_resolution=5
)
```

### `percentile_calculator.py` - Cálculo de Percentiles
Calcula percentiles con interpolación lineal:
- P5 (extremo bajo), P25 (óptimo bajo), P75 (óptimo alto), P95 (extremo alto)
- Para temperatura, precipitación y altitud

```python
from climatic.percentile_calculator import PercentileCalculator

percentiles = PercentileCalculator.calculate_climate_percentiles(
    temp_min_list=[...],
    temp_max_list=[...],
    rainfall_list=[...],
    altitude_list=[...]
)
```

---

## 🔌 Endpoints

### `routes/climatic.py`

Tres endpoints integrados con FastAPI y autenticación:

#### 1. **POST `/api/v1/climatic/calculate`**
Calcula sin guardar (preview)
```bash
curl -X POST http://localhost:8000/api/v1/climatic/calculate \
  -H "Authorization: Bearer TOKEN" \
  -d '{"id_species": 3, "sample_size": 50}'
```

#### 2. **POST `/api/v1/climatic/save`**
Guarda datos pre-calculados
```bash
curl -X POST http://localhost:8000/api/v1/climatic/save \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "id_species": 3,
    "temp_min": 5.2,
    ...
  }'
```

#### 3. **POST `/api/v1/climatic/calculate-and-save`** ⭐ RECOMENDADO
Calcula Y guarda en una operación
```bash
curl -X POST http://localhost:8000/api/v1/climatic/calculate-and-save \
  -H "Authorization: Bearer TOKEN" \
  -d '{"id_species": 3, "sample_size": 50}'
```

---

## 🚀 Uso Rápido

### Opción 1: Endpoint Web (Recomendado)
```bash
# Calcular para trigo (id_species=3) y guardar automáticamente
curl -X POST http://localhost:8000/api/v1/climatic/calculate-and-save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "id_species": 3,
    "sample_size": 30,
    "frost_tolerance": "high"
  }'
```

### Opción 2: Script Local
```bash
# Ejecutar pruebas locales (sin servidor)
python test_climate_niche.py
```

### Opción 3: Directo desde Python
```python
from climatic.climate_niche import ClimateNicheCalculator
from app.crud import crud_action

# Paso 1: Calcular
result = ClimateNicheCalculator.calculate(id_species=3)

# Paso 2: Guardar (opcional)
if "error" not in result:
    crud_action(
        action="create",
        table="climate_requirements",
        data=result
    )
```

---

## 📊 Interpretación de Resultados

Cada especie obtiene ** dos rangos** para cada parámetro:

| Campo | Significado |
|-------|-------------|
| `temp_min` (P5) | **Límite inferior** - No crece por debajo |
| `temp_opt_min` (P25) | **Óptimo mínimo** - Empieza a crecer bien |
| `temp_opt_max` (P75) | **Óptimo máximo** - Sigue creciendo bien |
| `temp_max` (P95) | **Límite superior** - Estrés por calor |

Ejemplo visual:
```
    Frío Extremo    Frío           Óptimo          Calor        Calor Extremo
    |———|————————|———————————|———————————|————————|————————|———|
    2°C  5.2°C  15.3°C      28.1°C      35.7°C  40°C
         ↑min                ↑opt_max
              ↑opt_min
                                         ↑max
```

---

## 📈 Performance

| Escenario | Tiempo | Puntos |
|-----------|--------|--------|
| Pocas ocurrencias | ~30 seg | <100 |
| Normal | ~1-2 min | 100-500 |
| Muchas ocurrencias | ~3-5 min | >500 |

**Factores:**
- Velocidad de Open-Meteo (50-60 seg si hay 50 puntos)
- Velocidad de Open-Elevation (5-10 seg)
- Velocidad de BD (< 1 seg)

---

## ⚙️ Personalización

### Cambiar período histórico
En `open_meteo_client.py`:
```python
# De 10 años a 20 años
start_date = (datetime.now() - timedelta(days=365 * 20)).strftime("%Y-%m-%d")
```

### Cambiar tamaño de grid
En `climate_niche.py`:
```python
# De 5° a 3° (más detallado)
sampled = GridSampler.stratified_random_sample(
    occurrences,
    sample_size=sample_size,
    grid_resolution=3  # ← Cambiar aquí
)
```

### Cambiar sample size automático
En `grid_sampling.py`:
```python
# De 20% a 30%
if sample_size is None:
    sample_size = max(10, int(len(occurrences) * 0.3))  # ← Cambiar aquí
```

---

## 🔍 Debugging

El módulo imprime logs detallados en la consola del servidor:

```
[1/5] Obteniendo ocurrencias para especie 3
  → 2341 ocurrencias encontradas

[2/5] Realizando muestreo estratificado
  → 48 puntos seleccionados después del muestreo

[3/5] Obteniendo datos climáticos de Open-Meteo
  → 25/48 puntos procesados
  → 47 puntos con datos climáticos válidos

[4/5] Obteniendo datos de altitud
  → 47 altitudes obtenidas

[5/5] Calculando percentiles
  ✓ Nicho climático calculado exitosamente
```

---

## 📚 Documentación

- **[CLIMATIC_NICHE.md](../CLIMATIC_NICHE.md)** - Guía de uso de endpoints
- **[CLIMATIC_TECHNICAL.md](../CLIMATIC_TECHNICAL.md)** - Documentación técnica
- **[test_climatic_curl.sh](../test_climatic_curl.sh)** - Ejemplos de CURL
- **[test_climate_niche.py](../test_climate_niche.py)** - Script de pruebas

---

## 🌐 APIs Externas

### Open-Meteo Archive
- ✅ Gratis, sin API key
- ✅ 10+ años de datos históricos
- ✅ Temperatura y precipitación diaria
- 📍 `https://archive-api.open-meteo.com/v1/archive`

### Open-Elevation
- ✅ Gratis, sin API key
- ✅ Datos DEM públicos
- ✅ ~1000 requests/día
- 📍 `https://api.open-elevation.com/api/v1/lookup`

---

## 🐛 Solución de Problemas

### Error: "No se encontraron ocurrencias"
→ La especie no tiene datos en la tabla `occurrences`
→ Verificar con: `SELECT * FROM occurrences WHERE id_species = ?`

### Error: "No se pudieron obtener datos climáticos"
→ Open-Meteo puede estar fuera de servicio
→ Coordenadas pueden ser inválidas (checar decimales)
→ Intentar de nuevo en unos segundos

### Campo `altitude_min/max` = NULL
→ Open-Elevation no encontró datos para esas coordenadas
→ Esto es normal en algunos casos (océanos, etc)
→ No causa error, solo omite ese dato

---

## 📋 Requisitos

- Python 3.8+
- FastAPI
- requests
- pymysql
- (Todos en `requirements.txt`)

---

## 🔐 Seguridad

- ✅ Autenticación requerida en todos los endpoints
- ✅ CRUD genérico validado
- ✅ No almacena credenciales de APIs externas
- ✅ Rate limiting implícito (APIs públicas limitan)

---

## 📝 Licencia e Integración

Módulo integrado en el proyecto Agro:
- Raíz: `/`
- Endpoints: registrados en `app/main.py`
- Datos: tabla `climate_requirements` del esquema existente
- CRUD: reutiliza `app.crud:crud_action`
- Auth: reutiliza `app.auth:auth_middleware`

---

## ✅ Checklist de Implementación

- [x] Módulo `climate_niche.py` - Orquestador
- [x] Módulo `open_meteo_client.py` - APIs climáticas
- [x] Módulo `open_elevation_client.py` - APIs altitud
- [x] Módulo `grid_sampling.py` - Muestreo estratificado
- [x] Módulo `percentile_calculator.py` - Percentiles
- [x] Router `routes/climatic.py` - Endpoints
- [x] Integración en `app/main.py` - Registro
- [x] Documentación: `CLIMATIC_NICHE.md`
- [x] Documentación: `CLIMATIC_TECHNICAL.md`
- [x] Script de test: `test_climate_niche.py`
- [x] Ejemplos CURL: `test_climatic_curl.sh`

---

## 🚀 Próximas Fases

Sugerencias para mejoras futuras:

**Fase 2: Optimización**
- Implementar caché Redis
- Paralelizar con asyncio
- Batch processing

**Fase 3: Features Avanzados**
- Predicciones climáticas (CMIP6)
- Cambio climático histórico
- Análisis de tendencias

**Fase 4: Visualización**
- Mapas interactivos (Folium, Plotly)
- Gráficos de percentiles
- Comparación entre especies

---

## 📞 Contacto

Para reportar issues o sugerencias, consular la documentación técnica o revisar los logs en consola.

¡Listo para usar! 🌾🌍
