# Traductor Semantico con IA - Documentacion

## Descripcion General

Sistema de traduccion inteligente que convierte nombres comunes a nombres cientificos usando OpenAI, con validacion automatica en GBIF para enriquecimiento agronomico.

### Flujo del Sistema

```
1. Usuario => "uva"
  |
2. IA (OpenAI) => "Vitis vinifera", "Vitis labrusca", "Vitis riparia"
  |
3. GBIF => validacion (confidence > 80%) y obtencion de datos taxonomicos
  |
4. Tu API => responde con datos normalizados
```

## Configuración

### 1. Variable de Entorno

En tu archivo `.env`, añade tu clave de OpenAI (licencia de paga):

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Nota**: Asegúrate de usar una clave de OpenAI con acceso al modelo GPT-4o.

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

Se incluye la librería `openai` en requirements.txt.

## Estructura de Carpetas

```
traductorsemantico_ia/
teacher __init__.py              # Inicializador del modulo
teacher config.py                # Configuracion y prompts
teacher translator.py            # Logica de traduccion con IA
teacher gbif_validator.py        # Validacion contra GBIF
```

## Endpoints API

### 1. Resolver Nombre Comun (POST)

**Endpoint**: `POST /api/v1/semantic/resolve-common-name`

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request body**:
```json
{
  "name": "uva"
}
```

**Ejemplo Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "uva"}' \
  "http://localhost:8000/api/v1/semantic/resolve-common-name"
```

**Ejemplo Response** (Exitoso - 200):
```json
{
  "commonName": "uva",
  "scientificNames": [
    {
      "inputName": "Vitis vinifera",
      "scientificName": "Vitis vinifera",
      "canonicalName": "Vitis vinifera",
      "taxonKey": 2883688,
      "rank": "SPECIES",
      "status": "ACCEPTED",
      "confidence": 98,
      "matchType": "EXACT",
      "phylum": "Tracheophyta",
      "scientificNameAuthorship": "L."
    },
    {
      "inputName": "Vitis labrusca",
      "scientificName": "Vitis labrusca",
      "canonicalName": "Vitis labrusca",
      "taxonKey": 2883673,
      "rank": "SPECIES",
      "status": "ACCEPTED",
      "confidence": 98,
      "matchType": "EXACT",
      "phylum": "Tracheophyta",
      "scientificNameAuthorship": "L."
    },
    {
      "inputName": "Vitis riparia",
      "scientificName": "Vitis riparia",
      "canonicalName": "Vitis riparia",
      "taxonKey": 2883689,
      "rank": "SPECIES",
      "status": "ACCEPTED",
      "confidence": 97,
      "matchType": "EXACT",
      "phylum": "Tracheophyta",
      "scientificNameAuthorship": "Michx."
    }
  ],
  "totalFound": 3
}
```

**Errores**:
- `400 Bad Request`: Nombre vacio
- `404 Not Found`: No se encontraron nombres validos en GBIF
- `500 Internal Server Error`: Error en OpenAI o GBIF

### 2. Resolver Lote de Nombres (POST)

**Endpoint**: `POST /api/v1/semantic/resolve-common-name-batch`

**Body**:
```json
{
  "names": ["uva", "manzana", "tomate", "lechuga"]
}
```

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Ejemplo Response** (200):
```json
{
  "totalRequests": 4,
  "successfulResolutions": 3,
  "results": [
    {
      "status": "success",
      "data": {
        "commonName": "uva",
        "scientificNames": [...],
        "totalFound": 3
      }
    },
    {
      "status": "error",
      "name": "fruta_inexistente",
      "error": "IA no pudo identificar nombres científicos para 'fruta_inexistente'"
    },
    ...
  ]
}
```

## Componentes del Sistema

### config.py

Define:
- **`build_prompt(common_name)`**: Construye el prompt para OpenAI
- **`GBIF_CONFIDENCE_THRESHOLD`**: Umbral mínimo de confianza (80%)
- **`GBIF_MATCH_ENDPOINT`**: URL de la API de GBIF

### translator.py

Clase `SemanticTranslator`:
- **`translate_to_scientific_names(common_name)`**: Traduce a 3 nombres científicos
- Usa GPT-4o para mayor precisión
- Temperatura baja (0.3) para consistencia
- Parseo automático de respuestas

### gbif_validator.py

Clase `GBIFValidator`:
- **`validate(scientific_name)`**: Valida un nombre científico
- **`validate_multiple(scientific_names)`**: Valida varios nombres
- Retorna datos normalizados de GBIF
- Solo acepta confianza > 80%

## Casos de Uso

### 1. Enriquecimiento de Base de Datos

Cuando un usuario ingresa un nombre comun:

```python
# 1. Resolver el nombre comun
response = requests.post(
    "http://api/api/v1/semantic/resolve-common-name",
    json={"name": "tomate"},
    headers={"Authorization": f"Bearer {token}"}
)

# 2. Usar el nombre cientifico validado para importar de GBIF
for sci_name in response.json()["scientificNames"]:
    # Importar de GBIF usando scientificName
    requests.post(
        "http://api/api/v1/gbif/import",
        json={"name": sci_name["scientificName"]},
        headers={"Authorization": f"Bearer {token}"}
    )
```

### 2. Busqueda Inteligente

Permitir a usuarios buscar por nombre comun y obtener resultados taxonomicos:

```bash
# Usuario busca "papa"
POST /api/v1/semantic/resolve-common-name
{
  "name": "papa"
}

# API retorna:
# - Solanum tuberosum (papa)
# - Solanum candidum
# - Solanum demissum
```

### 3. Validacion de Especies

Antes de almacenar una especie en la BD, validar que existe en GBIF:

```python
# Validar multiples nombres
response = requests.post(
    "http://api/api/v1/semantic/resolve-common-name-batch",
    json={"names": ["uva", "manzana", "tomate"]},
    headers={"Authorization": f"Bearer {token}"}
)

# Solo almacenar especies validadas
for result in response.json()["results"]:
    if result["status"] == "success":
        # Insertar en BD con datos de GBIF
        save_species(result["data"])
```

## Modelo de Datos

### Estructura de Respuesta

Cada nombre científico validado contiene:

```
{
  "inputName": str              # Nombre que envió IA
  "scientificName": str         # Nombre científico validado
  "canonicalName": str          # Nombre canónico
  "taxonKey": int              # ID de GBIF
  "rank": str                  # Rango taxonómico (SPECIES, GENUS, etc)
  "status": str                # Estado (ACCEPTED, SYNONYM, etc)
  "confidence": int            # Confianza de validación (0-100)
  "matchType": str             # Tipo de coincidencia (EXACT, FUZZY, etc)
  "phylum": str                # Filo taxonómico
  "scientificNameAuthorship": str  # Autor del nombre
}
```

## Ventajas del Sistema

OK - Precision: GPT-4o entiende contexto botanico
OK - Validacion: Confirmacion automatica con GBIF
OK - Escalabilidad: Procesa lotes de nombres
OK - Enriquecimiento: Obtiene datos taxonomicos completos
OK - Seguridad: Requiere autenticacion JWT
OK - Consistencia: Umbrales de confianza configurables  

## Limitaciones y Consideraciones

ADVERTENCIA - Costo de API: OpenAI cobra por uso (licencia de paga)
ADVERTENCIA - Latencia: Depende de disponibilidad de OpenAI y GBIF
ADVERTENCIA - Nombres Ambiguos: Algunos nombres comunes pueden tener multiplas especies
ADVERTENCIA - Idioma: Optimizado para nombres comunes en espanol  

## Troubleshooting

### Error: "OPENAI_API_KEY no esta configurada"

```bash
# Verificar que .env existe y contiene:
cat .env | grep OPENAI_API_KEY
```

### Error: "No se pudo validar ningun nombre cientifico en GBIF"

- El nombre cientifico puede ser incorrecto
- Aumentar `GBIF_CONFIDENCE_THRESHOLD` en config.py
- Especie muy rara o no catalogada en GBIF

### Error: "Rate limit exceeded"

- OpenAI: Esperar y reintentar (implementar exponential backoff)
- GBIF: Implementar cache de resultados

## Proximas Mejoras

CACHE - Cache de resultados (Redis)
CACHE - Traduccion automatica de idiomas
CACHE - Soporte para nombres comunes internacionales
CACHE - Enriquecimiento automatico al importar
CACHE - Dashboard de estadisticas de traducciones  

## Referencias

- [OpenAI API Docs](https://platform.openai.com/docs)
- [GBIF Species Match](https://www.gbif.org/es/tool/match)
- [GBIF Data API](https://data.gbif.org/developer/summary)
