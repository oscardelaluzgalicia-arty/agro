# 📁 Estructura Completa: Nicho Climático

```
agro/
│
├── 📄 IMPLEMENTATION_SUMMARY.md ✨ NEW
│   └── Resumen ejecutivo de toda la implementación
│
├── 📄 CLIMATIC_NICHE.md ✨ NEW
│   └── Guía de uso de endpoints (275 líneas)
│
├── 📄 CLIMATIC_TECHNICAL.md ✨ NEW
│   └── Documentación técnica en profundidad (580 líneas)
│
├── 🐍 test_climate_niche.py ✨ NEW
│   └── Script de pruebas locales (150 líneas)
│
├── 📜 test_climatic_curl.sh ✨ NEW
│   └── Ejemplos CURL listos para copiar (142 líneas)
│
├── 📁 app/
│   ├── 🐍 main.py ✏️ MODIFICADO
│   │   ├── from routes.climatic import router as climatic_router
│   │   └── app.include_router(climatic_router, ...)
│   ├── 🐍 crud.py
│   ├── 🐍 db.py
│   └── 🐍 auth.py
│
├── 📁 climatic/ ✨ NUEVA CARPETA
│   ├── 🐍 __init__.py ✨ NEW
│   │   └── Inicializador del módulo
│   │
│   ├── 🐍 climate_niche.py ✨ NEW (378 líneas)
│   │   ├── class ClimateNicheCalculator
│   │   ├── def calculate(id_species, sample_size)
│   │   │   ├── [1/5] Obtener ocurrencias
│   │   │   ├── [2/5] Muestreo inteligente
│   │   │   ├── [3/5] Clima histórico
│   │   │   ├── [4/5] Altitud
│   │   │   └── [5/5] Percentiles
│   │   └── def _get_occurrences(id_species)
│   │
│   ├── 🐍 open_meteo_client.py ✨ NEW (127 líneas)
│   │   ├── class OpenMeteoClient
│   │   ├── def get_climate_data(lat, lon, start_date, end_date)
│   │   │   └── GET https://archive-api.open-meteo.com/v1/archive
│   │   ├── def calculate_annual_stats(daily_data)
│   │   │   └── Retorna: temp_media_anual, precipitacion_anual_total
│   │   └── def extract_lists_for_percentiles(climate_data_list)
│   │       └── Retorna: (temp_min[], temp_max[], rainfall[])
│   │
│   ├── 🐍 open_elevation_client.py ✨ NEW (77 líneas)
│   │   ├── class OpenElevationClient
│   │   ├── def get_elevation(lat, lon)
│   │   │   └── GET https://api.open-elevation.com/api/v1/lookup
│   │   └── def get_elevations_batch(coords)
│   │       └── Batch de hasta 100 puntos por request
│   │
│   ├── 🐍 grid_sampling.py ✨ NEW (111 líneas)
│   │   ├── class GridSampler
│   │   ├── def get_grid_cell(lat, lon, resolution)
│   │   │   └── Retorna: "lat_lon" identificador
│   │   ├── def stratified_random_sample(occurrences, sample_size, grid_resolution)
│   │   │   ├── Grid 5° × 5°
│   │   │   ├── Agrupa ocurrencias
│   │   │   └── Muestreo aleatorio uniforme
│   │   └── def filter_outliers(values, percentiles)
│   │       └── Filtra valores extremos
│   │
│   ├── 🐍 percentile_calculator.py ✨ NEW (76 líneas)
│   │   ├── class PercentileCalculator
│   │   ├── def percentile(data, p)
│   │   │   └── Calcula P_p con interpolación lineal
│   │   └── def calculate_climate_percentiles(temp_min, temp_max, rainfall, altitude)
│   │       └── Retorna: {temp_min, temp_opt_min, temp_opt_max, temp_max, ...}
│   │
│   └── 📄 README.md ✨ NEW
│       └── Documentación del módulo climatic
│
├── 📁 routes/
│   ├── 🐍 climatic.py ✨ NEW (235 líneas)
│   │   ├── @router.post("/calculate")
│   │   │   ├── Input: {id_species, sample_size?}
│   │   │   └── Output: Dict percentiles (no guardado)
│   │   │
│   │   ├── @router.post("/save")
│   │   │   ├── Input: {id_species, temp_min, temp_opt_min, ...}
│   │   │   └── Output: {success: true, operation: "created|updated"}
│   │   │
│   │   └── @router.post("/calculate-and-save") ⭐ RECOMENDADO
│   │       ├── Input: {id_species, sample_size?, frost_tolerance?, ...}
│   │       └── Output: {success, niche_data, saved_data}
│   │       └── Ejecuta pipeline completo + guardado en una operación
│   │
│   ├── 🐍 gbif.py
│   ├── 🐍 semantic_translator.py
│   └── 🐍 grid_h3.py
│
└── 📁 (resto del proyecto sin cambios)
    ├── ...
    └── requirements.txt (sin cambios: requests ya incluido)
```

---

## 🔄 Flujo de Datos

```
REQUEST WEB
    ↓
┌─────────────────────────────────┐
│  /api/v1/climatic/calculate-and │
│  -save (POST)                   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  routes/climatic.py             │
│  calculate_and_save_climate_niche│
└─────────────────────────────────┘
    ↓
            ↓
┌────────────────────────────────────────────────────────────────┐
│  climate_niche.py: ClimateNicheCalculator.calculate()          │
├────────────────────────────────────────────────────────────────┤
│  [1/5] OBTENER OCURRENCIAS                                     │
│        crud_action(read, occurrences, where={id_species})      │
│        ↓                                                        │
│        → app/db.py: get_connection()                           │
│        → app/crud.py: crud_action()                            │
├────────────────────────────────────────────────────────────────┤
│  [2/5] MUESTREO INTELIGENTE                                    │
│        → grid_sampling.py: GridSampler.stratified_random_sample│
│        → Grid 5° × 5°                                          │
│        → Selecciona ~50 puntos distribuidos                    │
├────────────────────────────────────────────────────────────────┤
│  [3/5] CLIMA HISTÓRICO (Open-Meteo)                            │
│        → open_meteo_client.py: OpenMeteoClient.get_climate_data│
│        → Para cada punto: GET archive-api.open-meteo.com       │
│        → Datos: temp_min, temp_max, precipitation (10 años)    │
├────────────────────────────────────────────────────────────────┤
│  [4/5] ALTITUD (Open-Elevation)                                │
│        → open_elevation_client.py: OpenElevationClient         │
│        → GET api.open-elevation.com                            │
│        → Batch de 100 puntos max                               │
├────────────────────────────────────────────────────────────────┤
│  [5/5] PERCENTILES                                             │
│        → percentile_calculator.py: PercentileCalculator        │
│        → Calcula P5, P25, P75, P95                             │
│        → Para: T_min, T_max, Precip, Altitud                  │
└────────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  crud_action(create|update)      │
│  table: climate_requirements     │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  RESPONSE JSON {success: true, ...}
└──────────────────────────────────┘
```

---

## 📋 Archivos por Responsabilidad

### 🔌 Capa API (Endpoints)
```
routes/climatic.py
└── Maneja HTTP requests
    └── Valida input
    └── Orquesta cálculo o guardado
    └── Retorna JSON response
```

### ⚙️ Capa de Lógica (Orquestación)
```
climatic/climate_niche.py
└── Ejecuta pipeline de 5 pasos
    └── Coordina entre módulos
    └── Maneja errores
    └── Retorna datos crudos
```

### 🌍 Capa de Datos Externos
```
climatic/open_meteo_client.py       → Clima
climatic/open_elevation_client.py   → Altitud
```

### 🎯 Capa de Muestreo
```
climatic/grid_sampling.py
└── Estratificación geográfica
```

### 📊 Capa de Cálculo
```
climatic/percentile_calculator.py
└── Matemática de percentiles
```

### 💾 Capa de Persistencia (Existente)
```
app/crud.py        → CRUD genérico
app/db.py          → Conexión MySQL
```

---

## 🎯 Puntos Clave

### ✅ Reutilización de Código Existente
- CRUD genérico (`crud_action`) ← para read occurrences
- Conexión BD (`get_connection`) ← para inserts/updates
- Autenticación (`auth_middleware`) ← para proteger endpoints
- Tabla `climate_requirements` ← ya en migraciones

### ✅ Sin Dependencias Nuevas
- `requests` ← ya en requirements.txt
- Todas las demás en stdlib Python

### ✅ Sin Configuración Externa
- APIs públicas (no requieren claves)
- Configuración por defecto sensata
- Todo en variables configurables

### ✅ Manejo Robusto de Errores
- Valida ocurrencias
- Continúa si fallan puntos individuales
- Logs detallados en consola
- Respuestas JSON claras

---

## 🚀 Cómo Empezar

### 1. Verificar que el servidor está corriendo
```bash
python -m uvicorn app.main:app --reload
```

### 2. Obtener token
```bash
curl -X POST http://localhost:8000/login \
  -d '{"username": "admin", "password": "password"}'
```

### 3. Ejecutar el cálculo
```bash
curl -X POST http://localhost:8000/api/v1/climatic/calculate-and-save \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id_species": 3}'
```

### 4. Verificar resultado en BD
```sql
SELECT * FROM climate_requirements WHERE id_species = 3;
```

---

## 📊 Comparación: Antes vs Después

### ANTES
```
❌ No hay cálculo de nicho climático
❌ No hay análisis de rangos óptimos
❌ No hay integración con datos climáticos
❌ Datos de altitud no utilizados
```

### DESPUÉS
```
✅ Endpoint que calcula nicho automáticamente
✅ Rangos óptimos (P25-P75) y extremos (P5-P95)
✅ 10+ años de datos climáticos históricos
✅ Integración con Open-Meteo y Open-Elevation
✅ Datos almacenados en tabla climate_requirements
✅ Muestreo inteligente para evitar sesgos
✅ 3 opciones de uso (preview, save, calc-save)
```

---

## 🎓 Conceptos Aplicados

### Muestreo Estratificado
→ Divide espacio geográfico en estratos (grid)
→ Muestrea uniformemente de cada estrato
→ Evita clustering (que todo esté en una región)

### Percentiles vs Promedios
→ No usa promedios (afectados por outliers)
→ P5-P95 define rango de tolerancia
→ P25-P75 define rango óptimo

### Interpolación Lineal
→ Método estándar para percentiles continuos
→ Más preciso que ranking simple
→ Implementado en `percentile_calculator.py`

### Open Data
→ Open-Meteo: Archivo climático libre
→ Open-Elevation: DEM de dominio público
→ Sin restricciones de uso

---

## 📞 Archivos de Soporte

| Archivo | Audiencia | Propósito |
|---------|-----------|-----------|
| [CLIMATIC_NICHE.md](../CLIMATIC_NICHE.md) | Usuarios finales | Cómo usar endpoints |
| [CLIMATIC_TECHNICAL.md](../CLIMATIC_TECHNICAL.md) | Desarrolladores | Cómo funciona internamente |
| [climatic/README.md](README.md) | Desarrolladores | Referencia de módulos |
| [test_climatic_curl.sh](../test_climatic_curl.sh) | Testers | Ejemplos de testing |
| [test_climate_niche.py](../test_climate_niche.py) | Desarrolladores | Script de pruebas |
| [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) | PM/Lead | Resumen ejecutivo |

---

## ✅ Checklist Final

- [x] Módulo `climatic/` creado con 5 submódulos
- [x] Endpoints en `routes/climatic.py` con 3 opciones
- [x] Integración en `app/main.py`
- [x] Documentación: 5 archivos (1,400+ líneas)
- [x] Testing: Script local + CURL examples
- [x] Validaciones: Errores manejados
- [x] Seguridad: Autenticación required
- [x] APIs: Sin claves requeridas
- [x] BD: Reutiliza tabla existente
- [x] CRUD: Reutiliza función genérica

**¡IMPLEMENTACIÓN COMPLETA Y LISTA PARA USAR!** 🚀

---

Last updated: 2026-02-23
Status: ✅ Production Ready
