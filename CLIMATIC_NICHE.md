# Endpoint de Nicho Climático (Climate Niche)

## 📋 Descripción

Este módulo calcula automáticamente el **nicho climático** de una especie basándose en sus ocurrencias geográficas. 

Pipeline completo:
1. ✅ Obtiene coordenadas de ocurrencias desde BD
2. 🎯 Muestreo inteligente (grid estratificado) para evitar sesgos geográficos
3. 🌡️ Consulta clima histórico (10+ años) de Open-Meteo
4. ⛰️ Obtiene altitudes de Open-Elevation
5. 📊 Calcula percentiles (5%, 25%, 75%, 95%) para todos los parámetros
6. 💾 Guarda en tabla `climate_requirements`

---

## 🔌 Endpoints

### 1. **POST `/api/v1/climatic/calculate`**

Calcula el nicho climático **sin guardar** en BD (útil para preview)

**Request:**
```json
{
  "id_species": 9,
  "sample_size": 50
}
```

**Parámetros:**
- `id_species` ✅ (requerido): ID de la especie
- `sample_size` (opcional): Cantidad de puntos a muestrear. Default: 20% de ocurrencias (mínimo 10)

**Response:**
```json
{
  "id_species": 9,
  "temp_min": 8.2,
  "temp_opt_min": 17.4,
  "temp_opt_max": 26.1,
  "temp_max": 34.7,
  "rainfall_min": 420,
  "rainfall_opt_min": 780,
  "rainfall_opt_max": 1250,
  "rainfall_max": 2100,
  "altitude_min": 50,
  "altitude_max": 2400,
  "points_sampled": 45,
  "points_with_climate": 43
}
```

**Campos de respuesta:**
| Campo | Descripción |
|-------|-------------|
| `temp_min` | Temperatura mínima extrema (5° percentil) |
| `temp_opt_min` | Temperatura óptima mínima (25° percentil) |
| `temp_opt_max` | Temperatura óptima máxima (75° percentil) |
| `temp_max` | Temperatura máxima extrema (95° percentil) |
| `rainfall_min` | Precipitación mínima anual (5° percentil) |
| `rainfall_opt_min` | Precipitación óptima mínima (25° percentil) |
| `rainfall_opt_max` | Precipitación óptima máxima (75° percentil) |
| `rainfall_max` | Precipitación máxima anual (95° percentil) |
| `altitude_min` | Altitud mínima (5° percentil) |
| `altitude_max` | Altitud máxima (95° percentil) |
| `points_sampled` | Puntos seleccionados del muestreo |
| `points_with_climate` | Puntos con datos climáticos válidos |

---

### 2. **POST `/api/v1/climatic/save`**

Guarda un nicho climático **previamente calculado** en la BD

**Request:**
```json
{
  "id_species": 9,
  "temp_min": 8.2,
  "temp_opt_min": 17.4,
  "temp_opt_max": 26.1,
  "temp_max": 34.7,
  "rainfall_min": 420,
  "rainfall_opt_min": 780,
  "rainfall_opt_max": 1250,
  "rainfall_max": 2100,
  "altitude_min": 50,
  "altitude_max": 2400,
  "frost_tolerance": "moderate",
  "drought_tolerance": "low"
}
```

**Parámetros:**
- `id_species` ✅ (requerido)
- Todos los campos climáticos
- `frost_tolerance`, `drought_tolerance` (opcionales)

**Response:**
```json
{
  "success": true,
  "id_species": 9,
  "operation": "created",
  "data": { ... }
}
```

---

### 3. **POST `/api/v1/climatic/calculate-and-save` ⭐ RECOMENDADO**

**Calcula Y guarda todo en una sola operación** (lo más común)

**Request:**
```json
{
  "id_species": 9,
  "sample_size": 50,
  "frost_tolerance": "high",
  "drought_tolerance": "moderate"
}
```

**Response:**
```json
{
  "success": true,
  "id_species": 9,
  "operation": "created",
  "niche_data": {
    "id_species": 9,
    "temp_min": 8.2,
    "temp_opt_min": 17.4,
    ...
  },
  "saved_data": { ... }
}
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Calcular nicho para trigo (id_species: 3)

```bash
curl -X POST http://localhost:8000/api/v1/climatic/calculate-and-save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "id_species": 3,
    "sample_size": 30,
    "frost_tolerance": "high",
    "drought_tolerance": "moderate"
  }'
```

### Ejemplo 2: Datos crudos (sin guardar)

Para inspeccionar datos antes de guardar:

```bash
curl -X POST http://localhost:8000/api/v1/climatic/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "id_species": 9,
    "sample_size": 20
  }'
```

---

## 🔍 Algoritmo de Muestreo Inteligente

Para evitar **sesgos por clustering** (si todos los puntos están en una región):

1. **Divide el mundo en grid de 5° × 5°**
2. **Agrupa ocurrencias por celda**
3. **Selecciona aleatoriamente de cada celda** de manera uniforme
4. Garantiza cobertura geográfica

**Ejemplo:**
- Tienes 1000 puntos de trigo
- 800 en Argentina, 200 en China
- Muestreo inteligente: selecciona proporcionalmente de ambas regiones
- Evita que el nicho sea solo "Argentina"

---

## 🌍 Fuentes de Datos

### Open-Meteo Archive API
- **URL:** https://archive-api.open-meteo.com/
- **Datos:** Temperatura mín/máx daily, precipitación
- **Período:** 10+ años históricos
- **Sin API Key requerida** ✅
- **Rápido y confiable**

### Open-Elevation API
- **URL:** https://api.open-elevation.com/
- **Datos:** Altitud (DEM datos públicos)
- **Sin API Key requerida** ✅

---

## 📊 Percentiles Explicados

| Percentil | Significado | Uso |
|-----------|------------|-----|
| 5° (min) | Valor extremo bajo | Límite inferior de tolerancia |
| 25° (opt_min) | Rango óptimo bajo | Temperatura/lluvia preferida |
| 75° (opt_max) | Rango óptimo alto | Temperatura/lluvia preferida |
| 95° (max) | Valor extremo alto | Límite superior de tolerancia |

**Ejemplo para temperatura mínima:**
- **temp_min: 8.2°C** → La especie NO crecerá por debajo de esto
- **temp_opt_min: 17.4°C** → Empieza a crecer bien aquí
- **temp_opt_max: 26.1°C** → Sigue creciendo bien hasta aquí
- **temp_max: 34.7°C** → Estrés por calor por encima de esto

---

## ⚙️ Configuración y Customización

### Cambiar tamaño de muestreo

En [climate_niche.py](./climatic/climate_niche.py):

```python
# Línea ~47: Cambiar grid_resolution
sampled = GridSampler.stratified_random_sample(
    occurrences,
    sample_size=sample_size,
    grid_resolution=5  # ← Cambiar aquí (grados)
)
```

- `grid_resolution=2`: Más detallado, menos puntos por región
- `grid_resolution=10`: Más general, más cobertura

### Cambiar período histórico

En [open_meteo_client.py](./climatic/open_meteo_client.py):

```python
# Línea ~20: Cambiar timedelta
if not start_date:
    start_date = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")  # ← 10 años
```

---

## 🐛 Manejo de Errores

El endpoint devuelve errores claros:

```json
{
  "error": "No se encontraron ocurrencias para esta especie",
  "id_species": 999
}
```

Errores comunes:
- **No ocurrencias:** No hay datos de coordenadas para esa especie
- **Sin datos climáticos:** Open-Meteo no disponible o coordenadas inválidas
- **ID inválido:** Especie no existe en BD

---

## 📈 Performance

- **Especies con <100 puntos:** ~30 segundos
- **Especies con 100-500 puntos:** ~1-2 minutos
- **Especies con >500 puntos:** ~3-5 minutos

**Optimización:** El programa:
- ✅ Realiza muestreo (no usa todos los puntos)
- ✅ Cachearía resultados (si se implementa)
- ✅ Puede paralelizar consultas con asyncio

---

## 📎 Integración con Otros Módulos

Este módulo está integrado con:

- **CRUD genérico:** Para leer ocurrencias y guardar resultados
- **Tabla `climate_requirements`:** Almacenamiento principal
- **Tabla `occurrences`:** Fuente de coordenadas

---

## 🚀 Próximas Mejoras

- [ ] Cachear resultados de Open-Meteo
- [ ] Paralelizar solicitudes con asyncio
- [ ] Agregar soporte para H3 oficial
- [ ] Exportar a GeoJSON
- [ ] Visualización interactiva
- [ ] Análisis de cambio climático
