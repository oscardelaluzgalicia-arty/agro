# Documentación Técnica - Pipeline de Nicho Climático

## 🏗️ Estructura de Archivos

```
climatic/
├── __init__.py
├── climate_niche.py              # 🎯 Orquestador principal
├── open_meteo_client.py          # 🌡️ APIs para datos climáticos
├── open_elevation_client.py      # ⛰️ APIs para altitud
├── grid_sampling.py              # 🎯 Muestreo estratificado
└── percentile_calculator.py      # 📊 Cálculo de percentiles

routes/
└── climatic.py                   # 🔌 Endpoints FastAPI
```

---

## 🔄 Flujo de Datos (Pipeline)

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUEST WEB API                           │
│  POST /api/v1/climatic/calculate-and-save                   │
│  { "id_species": 3, "sample_size": 50 }                     │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [1] OBTENER OCURRENCIAS                                    │
│  - Query: SELECT * FROM occurrences WHERE id_species = 3    │
│  - Resultado: Lista de coordenadas (lat, lon, elevation)    │
│  └─ App: OpenCRUD generic action                            │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [2] MUESTREO INTELIGENTE POR GRID                          │
│  - Divide mundo en celdas 5° × 5°                           │
│  - Agrupa ocurrencias por celda                             │
│  - Selecciona aleatoriamente de cada celda                  │
│  └─ Resultado: ~50 puntos distribuidos geográficamente      │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [3] OBTENER CLIMA HISTÓRICO (Open-Meteo)                  │
│  - Para cada punto: GET /v1/archive?lat,lon,start,end       │
│  - Datos: temperature_2m_min/max, precipitation_sum         │
│  - Período: Últimos 10 años (configurable)                  │
│  - Resultado: Arrays de valores diarios para cada punto      │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [4] OBTENER ALTITUD (Open-Elevation)                       │
│  - Para cada punto: GET /api/v1/lookup?locations=lat,lon    │
│  - Batch de ~100 puntos por request                         │
│  - Resultado: Lista de altitudes en metros                  │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [5] EXTRAER LISTAS DE DATOS                                │
│  - Temperatura mínima: [5.2, 6.1, 7.3, ..., 35.2]           │
│  - Temperatura máxima: [12.1, 13.4, ..., 38.9]              │
│  - Precipitación: [0, 2.3, 5.1, ..., 50.2]                  │
│  - Altitud: [50, 120, 450, ..., 2400]                       │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────┐
│  [6] CALCULAR PERCENTILES                                   │
│  ┌─ 5° (mín extremo)    ─────────┐                          │
│  │ 25° (rango óptimo bajo)       │                          │
│  │ 75° (rango óptimo alto)       │                          │
│  └─ 95° (máx extremo)    ────────┘                          │
│                                                              │
│  Resultado para CADA parámetro:                             │
│  {                                                          │
│    "temp_min": 5.2,          # P5 de temp_min              │
│    "temp_opt_min": 15.3,     # P25 de temp_min             │
│    "temp_opt_max": 28.1,     # P75 de temp_max             │
│    "temp_max": 35.7,         # P95 de temp_max             │
│    "rainfall_min": 150,      # P5 de precip                │
│    "rainfall_opt_min": 600,  # P25 de precip               │
│    "rainfall_opt_max": 1100, # P75 de precip               │
│    "rainfall_max": 1800,     # P95 de precip               │
│    "altitude_min": 50,       # P5 de altitud               │
│    "altitude_max": 2400      # P95 de altitud              │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ⬇️
┌──────────────────────────────────────────────────────────────┐
│  [7] GUARDAR EN BD                                           │
│  - INSERT INTO climate_requirements (id_species, ...)        │
│  - O UPDATE si ya existe                                     │
│  - Tabla: climate_requirements                               │
│  - FK: especies.id_species                                   │
│  └─ Status: 200 OK + JSON response                          │
└──────────────────────────────────────────────────────────────┘
                            ⬇️
┌──────────────────────────────────────────────────────────────┐
│                    RESPUESTA JSON                             │
│  {                                                            │
│    "success": true,                                           │
│    "id_species": 3,                                           │
│    "operation": "created",                                    │
│    "niche_data": {...},                                       │
│    "saved_data": {...}                                        │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Matriz de Percentiles

### Concepto General

Para cada variable (T_min, T_max, Precipitación, Altitud):

```
0%          5%               25%              75%              95%         100%
|———————————|———————————|————————————|————————————|———————————|———————|
MIN      EXTREMO    ÓPTIMO_MIN   ÓPTIMO_MAX    EXTREMO          MAX
(raro)    BAJO       BAJO         ALTO          ALTO             (raro)
```

### Ejemplo: Trigo (Triticum aestivum)

**Temperatura Mínima:**
```
2°C      5.2°C        15.3°C       (no aplica)   (no aplica)      20°C
|———————|———————|—————————|————————————————————————————————————————————|
 Heladas Crítico Crece Bien  (se calcula de temp_min histórico)
```

**Temperatura Máxima:**
```
10°C     12°C    (no aplica)    28.1°C       35.7°C            40°C
|———————|————————|————————————————————————|—————————|————————————————|
        Frío    (se calcula de temp_max histórico)  Calor Extremo
```

**Precipitación Anual:**
```
0mm      150mm       600mm        1100mm       1800mm          2500mm
|———————|———————|————————————————|————————————————|————————|—————————|
 Sequía  Min  Moderada Lluvia   Óptimo       Abundante Saturación
```

---

## 🔧 Clases Principales

### 1. `ClimateNicheCalculator`
**Archivo:** `climate_niche.py`
```python
class ClimateNicheCalculator:
    @staticmethod
    def calculate(id_species: int, sample_size: int = None) -> Dict
    # Ejecuta todo el pipeline y retorna dict con percentiles
    
    @staticmethod
    def _get_occurrences(id_species: int) -> List[Dict]
    # Helper: obtiene ocurrencias del CRUD
```

### 2. `OpenMeteoClient`
**Archivo:** `open_meteo_client.py`
```python
class OpenMeteoClient:
    @staticmethod
    def get_climate_data(lat: float, lon: float, ...) -> Dict
    # Obtiene datos diarios históricos de Open-Meteo
    
    @staticmethod
    def calculate_annual_stats(daily_data: Dict) -> Dict
    # Calcula temp_media_anual, precipitacion_anual_total
    
    @staticmethod
    def extract_lists_for_percentiles(climate_data_list: List[Dict]) -> Tuple
    # Genera listas continuas de valores para percentiles
```

### 3. `OpenElevationClient`
**Archivo:** `open_elevation_client.py`
```python
class OpenElevationClient:
    @staticmethod
    def get_elevation(lat: float, lon: float) -> float
    # Obtiene altitud para UN punto
    
    @staticmethod
    def get_elevations_batch(coords: List[tuple]) -> List[float]
    # Obtiene altitudes para múltiples puntos (hasta 100 por request)
```

### 4. `GridSampler`
**Archivo:** `grid_sampling.py`
```python
class GridSampler:
    @staticmethod
    def get_grid_cell(lat: float, lon: float, resolution: int) -> str
    # Retorna identificador de celda "lat_lon"
    
    @staticmethod
    def stratified_random_sample(occurrences: List[Dict], ...) -> List[Dict]
    # Muestreo estratificado por grid
    
    @staticmethod
    def filter_outliers(values: List[float], ...) -> List[float]
    # Filtra valores extremos por percentiles
```

### 5. `PercentileCalculator`
**Archivo:** `percentile_calculator.py`
```python
class PercentileCalculator:
    @staticmethod
    def percentile(data: List[float], p: int) -> float
    # Calcula percentil p (0-100) con interpolación lineal
    
    @staticmethod
    def calculate_climate_percentiles(temp_min, temp_max, rainfall, altitude) -> Dict
    # Calcula todos los percentiles (5, 25, 75, 95) para todos los parámetros
```

---

## 🔌 Endpoints (Routes)

**Archivo:** `routes/climatic.py`

### POST `/api/v1/climatic/calculate`
- **Input:** `{ "id_species": int, "sample_size": int? }`
- **Output:** Dict con percentiles (sin guardar en BD)
- **Usado para:** Preview antes de guardar

### POST `/api/v1/climatic/save`
- **Input:** Dict completo con todos los percentiles
- **Output:** `{ "success": true, "operation": "created|updated" }`
- **Usado para:** Guardar datos pre-calculados

### POST `/api/v1/climatic/calculate-and-save` ⭐
- **Input:** `{ "id_species": int, "sample_size": int? }`
- **Output:** Datos calculados + confirmación de guardado
- **Usado para:** Flujo completo en una sola llamada

---

## 📈 Complejidad Algorítmica

| Operación | Complejidad | Tiempo Estimado |
|-----------|------------|-----------------|
| Obtener ocurrencias (BD) | O(n) | 1-2 seg |
| Muestreo por grid | O(n log n) | 1 seg |
| Consultas climáticas | O(m * k) * API | 1-3 min |
| Consultas altitud | O(m / 100) * API | 10-20 seg |
| Percentiles | O(n log n) | <1 seg |
| **TOTAL** | - | **~2-4 min** |

Donde:
- n = ocurrencias totales
- m = ocurrencias muestreadas (~50-100)
- k = llamadas API por punto

---

## 🌐 Integraciones Externas

### Open-Meteo Archive API
- **Endpoint:** `https://archive-api.open-meteo.com/v1/archive`
- **Parámetros:**
  - `latitude, longitude` (coordinadas)
  - `start_date, end_date` (formato YYYY-MM-DD)
  - `daily` = "temperature_2m_min,temperature_2m_max,precipitation_sum"
- **Rate Limit:** No identificado (probablemente ilimitado)
- **Timeout:** 30 segundos por request

### Open-Elevation API
- **Endpoint:** `https://api.open-elevation.com/api/v1/lookup`
- **Parámetros:**
  - `locations` = "lat,lon|lat,lon|..." (hasta 100 puntos)
- **Rate Limit:** ~1000/día, prudente usar <100 por batch
- **Timeout:** 10-30 segundos por request

---

## 💾 Esquema de BD

**Tabla: `climate_requirements`**

```sql
CREATE TABLE climate_requirements (
  id_climate BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_species BIGINT NOT NULL UNIQUE,
  
  -- Temperatura (5, 25, 75, 95 percentiles)
  temp_min FLOAT COMMENT '5° percentil de temp mínima',
  temp_opt_min FLOAT COMMENT '25° percentil',
  temp_opt_max FLOAT COMMENT '75° percentil',
  temp_max FLOAT COMMENT '95° percentil de temp máxima',
  
  -- Precipitación (mismo patrón)
  rainfall_min FLOAT,
  rainfall_opt_min FLOAT,
  rainfall_opt_max FLOAT,
  rainfall_max FLOAT,
  
  -- Altitud (solo 5 y 95)
  altitude_min FLOAT,
  altitude_max FLOAT,
  
  -- Tolerancias opcionales
  frost_tolerance VARCHAR(50),
  drought_tolerance VARCHAR(50),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (id_species) REFERENCES species(id_species)
);
```

---

## ⚙️ Configuración por Defecto

| Parámetro | Valor | Ubicación |
|-----------|-------|-----------|
| Grid resolution | 5° × 5° | `climate_niche.py:47` |
| Período histórico | 10 años | `open_meteo_client.py:20` |
| Sample size % | 20% | `climate_niche.py:68` |
| Sample size mínimo | 10 puntos | `grid_sampling.py:75` |
| Open-Meteo timeout | 30 seg | `open_meteo_client.py:35` |
| Open-Elevation timeout | 10 seg | `open_elevation_client.py:27` |
| Batch altitud | 100 puntos | `open_elevation_client.py:48` |

---

## 🚨 Manejo de Errores

### Estrategia de Resiliencia

1. **Sin ocurrencias:** ✅ Error claro, no procesa
2. **Sin datos climáticos:** ✅ Continúa con puntos válidos
3. **Altitud no disponible:** ✅ Campo `altitude_min/max` = NULL
4. **API timeout:** ✅ Retorna último resultado parcial

### Mensajes de Error

```python
{
  "error": "No se encontraron ocurrencias para esta especie",
  "id_species": 999
}
```

---

## 📊 Ejemplo de Respuesta Completa

```json
{
  "success": true,
  "id_species": 3,
  "operation": "created",
  "niche_data": {
    "id_species": 3,
    "temp_min": 5.2,
    "temp_opt_min": 15.3,
    "temp_opt_max": 28.1,
    "temp_max": 35.7,
    "rainfall_min": 150.0,
    "rainfall_opt_min": 600.0,
    "rainfall_opt_max": 1100.0,
    "rainfall_max": 1800.0,
    "altitude_min": 50.0,
    "altitude_max": 2400.0,
    "points_sampled": 48,
    "points_with_climate": 47
  },
  "saved_data": {
    "id_species": 3,
    "temp_min": 5.2,
    ...
  }
}
```

---

## 🔍 Debugging y Logs

El servidor imprime logs en consola:

```
[1/5] Obteniendo ocurrencias para especie 3
  → 2341 ocurrencias encontradas

[2/5] Realizando muestreo estratificado
  → 48 puntos seleccionados después del muestreo

[3/5] Obteniendo datos climáticos de Open-Meteo
  → 5/48 puntos procesados
  → 10/48 puntos procesados
  → 47 puntos con datos climáticos válidos

[4/5] Obteniendo datos de altitud
  → 47 altitudes obtenidas

[5/5] Calculando percentiles
  ✓ Nicho climático calculado exitosamente
```

---

## 🚀 Mejoras Futuras

1. **Cache de resultados:** Redis para no recalcular
2. **Async/await:** Paralelizar requests con asyncio
3. **Actualización incremental:** solo nuevas ocurrencias
4. **Historiales:** guardar cambios en el tiempo
5. **Predicción climática:** integrar CMIP6 projections
6. **Visualización:** mapas interactivos de nichos
7. **Validación:** comparar con observaciones de expertos
