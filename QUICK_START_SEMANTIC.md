## Quick Start - Traductor Semantico

### 1. Configurar OpenAI API Key

Edita tu `.env` y reemplaza `your-api-key-here` con tu clave real:

```env
OPENAI_API_KEY=sk-proj-tu-clave-aqui
```

Para obtener tu clave:
1. Ve a https://platform.openai.com/account/api-keys
2. Crea una nueva clave de API
3. Cópiala en `.env`

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará `openai` y todas las dependencias.

### 3. Probar el Sistema

```bash
# Ejecutar pruebas automáticas
python test_semantic_translator.py
```

Output esperado:
```
OK - Configuracion
OK - Translator
OK - Validator
OK - Pipeline Completo

Total: 4/4 pruebas exitosas
```

### 4. Iniciar la API

```bash
# Desde el directorio raíz
uvicorn app.main:app --reload --port 8000
```

### 5. Probar los Endpoints

#### Opción A: Con curl

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/v1/semantic/resolve-common-name?name=uva"
```

#### Opción B: Con Python

```python
import requests

token = "YOUR_JWT_TOKEN"
response = requests.get(
    "http://localhost:8000/api/v1/semantic/resolve-common-name",
    params={"name": "uva"},
    headers={"Authorization": f"Bearer {token}"}
)

print(response.json())
```

#### Opción C: Con el script ejemplo

```bash
python example_semantic_enrichment.py
```

### 📊 Estructura de Respuesta

```json
{
  "commonName": "uva",
  "scientificNames": [
    {
      "scientificName": "Vitis vinifera",
      "confidence": 98,
      "rank": "SPECIES",
      "status": "ACCEPTED",
      "taxonKey": 2883688
    }
  ],
  "totalFound": 3
}
```

### 📚 Documentación Completa

Para más detalles, consulta [SEMANTIC_TRANSLATOR.md](SEMANTIC_TRANSLATOR.md)

### 🐛 Troubleshooting

**Error: "OPENAI_API_KEY no está configurada"**
- Revisa que `.env` tenga la variable configurada
- Reinicia la aplicación después de editar `.env`

**Error: "No se pudo validar ningún nombre científico en GBIF"**
- Prueba con nombres más comunes (uva, manzana, tomate)
- Algunos nombres raros o locales no están en GBIF

**Error: "Rate limit exceeded"**
- Espera unos minutos y reinténtalo
- Implementa caché para reducir llamadas repetidas

### ✨ Casos de Uso

1. **Busqueda inteligente**: Usuario dice "uva" => obtiene "Vitis vinifera"
2. **Enriquecimiento**: Importa automaticamente datos de GBIF
3. **Validacion**: Verifica que el nombre existe antes de guardar en BD
4. **Proyecciones**: Mejora analisis agronomicos con datos consistentes
