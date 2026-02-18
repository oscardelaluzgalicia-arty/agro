# Pipeline Paralelo de Enriquecimiento Agronómico

## Descripción

Pipeline de enriquecimiento automático que infiere características agronómicas de una especie basándose en:
- **Datos almacenados** de ocurrencias geográficas (coordenadas)
- **Datos climáticos** de WorldClim (via Open-Meteo API)
- **Heurísticas** basadas en familia botánica e información existente

## Arquitectura

### 8 Pasos Ejecutados en Paralelo

```
INPUT: id_species

├─ [1] Obtener datos base de especie
│  └─ id_species, scientific_name, genus, family
│
├─ [2] Obtener ocurrencias almacenadas
│  └─ decimal_latitude, decimal_longitude, event_date, month
│
├─ [3] Enriquecer con WorldClim (PARALELO por coordenada)
│  ├─ Temperatura media anual
│  ├─ Precipitación anual
│  └─ Altitud
│
├─ [4] Insertar climate_requirements
│  ├─ Percentiles: 5%, 25%, 75%, 95%
│  ├─ Rangos óptimos
│  └─ Tolerancias (helada, sequía)
│
├─ [5] Insertar crop_profile
│  ├─ crop_type
│  ├─ planting_method
│  ├─ sunlight_requirement
│  ├─ water_requirement
│  └─ nitrogen_fixing (si family == Fabaceae)
│
├─ [6] Insertar soil_requirements
│  ├─ pH range (5.5-7.5)
│  ├─ soil_texture (loam)
│  ├─ drainage
│  └─ organic_matter_need
│
├─ [7] Insertar planting_calendar
│  ├─ Analiza distribución mensual de ocurrencias
│  ├─ Identifica mes pico (cosecha)
│  └─ Infiere siembra 4-6 meses antes
│
└─ [8] Insertar companion_plants
   └─ Basada en familia botánica
      ├─ Fabaceae → Gramíneas (nitrogen_fixing)
      └─ Poaceae → Legumbres + Cucurbitaceas (compatible)
```

## Cálculo de Percentiles Climáticos

Para todas las ocurrencias de una especie:

```python
temps = [temp de cada coordenada]
rains = [precip de cada coordenada]
alts = [altitud de cada coordenada]

temp_min      = percentile(temp, 5)      # Límite inferior
temp_opt_min  = percentile(temp, 25)     # Óptimo inferior
temp_opt_max  = percentile(temp, 75)     # Óptimo superior
temp_max      = percentile(temp, 95)     # Límite superior

# Lo mismo para rainfall y altitude
```

## API Endpoint

### POST `/api/v1/enrich/agronomy`

**Request:**
```json
{
  "id_species": 1
}
```

**Response (Éxito):**
```json
{
  "id_species": 1,
  "species_name": "Zea mays",
  "timestamp": "2026-02-17T10:30:45.123456",
  "operations": {
    "climate": {
      "status": "inserted",
      "params": {
        "temp_min": 8.5,
        "temp_opt_min": 15.2,
        "temp_opt_max": 28.7,
        "temp_max": 35.2,
        "rainfall_min": 200,
        "rainfall_opt_min": 400,
        "rainfall_opt_max": 800,
        "rainfall_max": 1200,
        "altitude_min": 50,
        "altitude_max": 2500
      }
    },
    "crop_profile": {
      "status": "inserted",
      "nitrogen_fixing": false
    },
    "soil": {
      "status": "inserted"
    },
    "calendar": {
      "status": "inserted",
      "peak_month": 9,
      "month_distribution": {7: 45, 8: 120, 9: 180, 10: 95}
    },
    "companions": {
      "status": "inserted",
      "count": 2,
      "inserted": [
        {
          "id_species_a": 1,
          "id_species_b": 4,
          "benefit": "nitrogen_fixing"
        }
      ]
    }
  }
}
```

**Response (Error):**
```json
{
  "error": "Especie no encontrada",
  "id_species": 999
}
```

## Ejemplo de Uso

### Con cURL
```bash
curl -X POST http://localhost:8000/api/v1/enrich/agronomy \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "id_species": 1
  }'
```

### Con Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/enrich/agronomy",
    json={"id_species": 1},
    headers={"Authorization": f"Bearer {token}"}
)

result = response.json()
print(f"Especie: {result['species_name']}")
print(f"Clima insertado: {result['operations']['climate']['status']}")
```

### Con JavaScript
```javascript
const response = await fetch('/api/v1/enrich/agronomy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ id_species: 1 })
});

const result = await response.json();
console.log(`Especie: ${result.species_name}`);
```

## Restricciones y Consideraciones

### Datos Faltantes
- Si la especie no tiene ocurrencias, se omite el enriquecimiento climático
- Los valores de soil y companion son valores por defecto/heurísticos
- Si WorldClim no responde, se usa data aproximada

### Llamadas Paralelas
- **Dentro del pipeline**: Las 5 inserciones (pasos 4-8) pueden ejecutarse en paralelo
- **Dentro de WorldClim**: Cada coordenada se consulta en paralelo via aiohttp
- **Rate limiting**: Open-Meteo tiene límite de ~10,000 requests/día compartido

### Transacciones
- Cada inserción es una transacción independiente
- Si una falla, las otras continúan (no transactional a nivel de pipeline)
- Para operaciones críticas, se puede implementar rollback completo

### Autenticación
- Requiere token válido (vía middleware `auth_middleware`)
- El token se envía en header `Authorization: Bearer {token}`

## Tablas Creadas

```sql
CREATE TABLE climate_requirements
- id_species
- temp_min, temp_opt_min, temp_opt_max, temp_max
- rainfall_min, rainfall_opt_min, rainfall_opt_max, rainfall_max
- altitude_min, altitude_max
- frost_tolerance, drought_tolerance

CREATE TABLE crop_profile
- id_species
- crop_type, planting_method
- sunlight_requirement, water_requirement
- nitrogen_fixing

CREATE TABLE soil_requirements
- id_species
- ph_min, ph_max
- soil_texture, drainage
- salinity_tolerance, organic_matter_need

CREATE TABLE planting_calendar
- id_species
- planting_start_month, planting_end_month
- harvest_start_month, harvest_end_month
-region_type, hemisphere

CREATE TABLE companion_plants
- id_species_a, id_species_b
- relationship_type, benefit_type
```

## Mejoras Futuras

- [ ] Integración real con WorldClim API (rasterio + GeoTIFF)
- [ ] Machine Learning para predicción de tolerancias
- [ ] Validación de datos climáticos (outliers)
- [ ] Support para múltiples regiones hemisféricas
- [ ] Cache de resultados WorldClim
- [ ] Batch processing para múltiples especies
- [ ] Webhooks para notificación de completitud
- [ ] Logs de auditoría
