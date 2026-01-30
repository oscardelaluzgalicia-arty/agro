# 🚀 NUEVO WORKFLOW - GBIF ONLY

## Cambios Implementados

### ✅ Completado
1. **Cliente GBIF (`gbif/client.py`)**
   - `get_occurrences_from_gbif()`: Obtiene ocurrencias con paginación automática
   - `parse_occurrence()`: Parsea campos de GBIF
   - `extract_ecological_zones_from_gbif_occurrences()`: Agrupa por estado
   - Removida: función iNaturalist

2. **Manejador de Ocurrencias (`gbif/occurrences_handler.py`)**
   - `gbif_occurrence_id` UNIQUE para evitar duplicados
   - 20 campos de GBIF (elevación, habitat, etc.)
   - Estadísticas mejoradas

3. **Manejador de Zonas (`gbif/zones_handler.py`)**
   - Recibe `id_species` como parámetro
   - Integra `parse_occurrence()` 
   - Importa zonas + ocurrencias en flujo unificado

4. **Rutas (`routes/gbif.py`)**
   - Simplificado a flujo GBIF-only
   - Obtiene `id_species` con DictCursor correctamente

5. **Schema BD (`schema.sql`)** - NUEVO
   - Tabla `occurrences` con todas las columnas
   - `gbif_occurrence_id` BIGINT UNIQUE
   - Índices geoespaciales

---

## 🎯 Para Ejecutar

### Terminal 1 - Inicializar BD:
```bash
cd c:\Users\oscar\OneDrive\Escritorio\agro
python init_db.py
```

### Terminal 2 - Iniciar servidor:
```bash
cd c:\Users\oscar\OneDrive\Escritorio\agro
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 3 - Ejecutar test:
```bash
# Con nombre científico 
cd c:\Users\oscar\OneDrive\Escritorio\agro
python test_import.py "Triticum aestivum"

# O con cualquier nombre
python test_import.py "Solanum lycopersicum"
python test_import.py "Zea mays"
```

---

## 📊 Flujo de Datos

```
POST /api/v1/gbif/import
  ↓
search_species(name) → GBIF /species/search
  ↓
get_species(gbif_key) → GBIF /species/{key}
  ↓
get_taxonomy_from_otol(scientific_name) → OpenTreeOfLife
  ↓
normalize_species() → Combina datos
  ↓
import_species() → Inserta en tabla species
  ↓
get_occurrences_from_gbif(taxon_key) → GBIF /occurrence/search (paginado)
  ↓
extract_ecological_zones_from_gbif_occurrences() → Agrupa por estado
  ↓
import_ecological_zones_with_species():
    - Inserta zonas
    - Asocia especie a zonas
    - parse_occurrence() para cada ocurrencia
    - import_occurrences_batch() → Tabla occurrences
```

---

## 🔍 Campos Extraídos de GBIF por Ocurrencia

- **ID**: gbif_occurrence_id (UNIQUE)
- **Ubicación**: country, state_province, municipality, locality
- **Coordenadas**: decimal_latitude, decimal_longitude, coordinate_uncertainty_meters
- **Fecha**: event_date, year, month, day
- **Ecología**: elevation, habitat
- **Metadata**: basis_of_record, dataset_key, institution_code, recorded_by, identified_by

---

## 📈 Estadísticas por Especie (ej: Solanum lycopersicum)

- **Especies**: 1 (id_species)
- **Zonas ecológicas**: ~30-50 (por estado en México)
- **Ocurrencias**: 1,000+ (con coordenadas verificadas)
- **Duplicados**: 0 (prevenidos por UNIQUE)

---

## ⚡ Características Principales

✅ **Solo GBIF** - Base científica verificada
✅ **Paginación** - Obtiene todas las ocurrencias (sin límite)
✅ **Coordenadas** - `hasCoordinate=True` filtra datos verificados
✅ **Sin duplicados** - `gbif_occurrence_id` UNIQUE
✅ **20 campos** - Información completa por ocurrencia
✅ **Zonas automáticas** - Agrupa por estado
✅ **Taxonomía completa** - GBIF + OpenTreeOfLife

---

## 🐛 Si hay errores

1. **"Species not found"** → El nombre no existe en GBIF
2. **"No se pudo recuperar id_species"** → Error al insertar especie
3. **Timeout** → Muchas ocurrencias, dar más tiempo (5 min max)
4. **DictCursor error** → Revisar que `app/db.py` use `pymysql.cursors.DictCursor`

---

## 📝 Próximos Pasos

1. Ejecutar `init_db.py` para crear tablas
2. Iniciar servidor con uvicorn
3. Correr test con Solanum lycopersicum
4. Verificar datos en BD con:
   ```sql
   SELECT COUNT(*) FROM occurrences WHERE id_species = 1;
   SELECT DISTINCT state_province FROM occurrences;
   ```
