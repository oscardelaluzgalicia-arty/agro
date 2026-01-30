"""
Módulo para manejar la importación de ocurrencias a la base de datos
Almacena datos de distribución geográfica y temporal de especies
"""
from app.db import get_connection


def insert_occurrence(conn, occurrence_data: dict) -> bool:
    """
    Inserta una ocurrencia individual en la tabla occurrences
    
    occurrence_data debe contener (del parser):
    - gbif_occurrence_id: ID único de GBIF (UNIQUE)
    - id_species: ID de la especie
    - decimal_latitude, decimal_longitude: Coordenadas (requeridas)
    - country, state_province: Ubicación
    - event_date, year, month, day: Fecha
    - locality, municipality: Descripción de ubicación
    - elevation, habitat: Detalles ecológicos
    - basis_of_record, dataset_key, institution_code: Metadata
    - recorded_by, identified_by: Responsables
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT IGNORE INTO occurrences 
                (gbif_occurrence_id, id_species, decimal_latitude, decimal_longitude,
                 coordinate_uncertainty_meters, country, state_province, municipality,
                 locality, event_date, year, month, day, habitat, elevation,
                 basis_of_record, dataset_key, institution_code, recorded_by, identified_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    occurrence_data.get("gbif_occurrence_id"),
                    occurrence_data.get("id_species"),
                    occurrence_data.get("decimal_latitude"),
                    occurrence_data.get("decimal_longitude"),
                    occurrence_data.get("coordinate_uncertainty_meters"),
                    occurrence_data.get("country"),
                    occurrence_data.get("state_province"),
                    occurrence_data.get("municipality"),
                    occurrence_data.get("locality"),
                    occurrence_data.get("event_date"),
                    occurrence_data.get("year"),
                    occurrence_data.get("month"),
                    occurrence_data.get("day"),
                    occurrence_data.get("habitat"),
                    occurrence_data.get("elevation"),
                    occurrence_data.get("basis_of_record"),
                    occurrence_data.get("dataset_key"),
                    occurrence_data.get("institution_code"),
                    occurrence_data.get("recorded_by"),
                    occurrence_data.get("identified_by"),
                )
            )
            return cur.rowcount > 0
    except Exception as e:
        print(f"⚠️ Error insertando ocurrencia: {e}")
        return False


def import_occurrences_batch(occurrences_list: list) -> dict:
    """
    Importa un lote de ocurrencias a la base de datos
    Para crear mapas de distribución geográfica
    
    Usa INSERT IGNORE para evitar duplicados via gbif_occurrence_id UNIQUE
    """
    conn = get_connection()
    stats = {
        "inserted": 0,
        "duplicated": 0,
        "errors": 0
    }
    
    try:
        print(f"\n📍 Importando {len(occurrences_list)} ocurrencias de GBIF...")
        
        for occ in occurrences_list:
            try:
                # Validar datos esenciales
                if not occ.get("gbif_occurrence_id"):
                    stats["errors"] += 1
                    continue
                
                if not (occ.get("decimal_latitude") and occ.get("decimal_longitude")):
                    stats["errors"] += 1
                    continue
                
                if insert_occurrence(conn, occ):
                    stats["inserted"] += 1
                else:
                    stats["duplicated"] += 1
                    
            except Exception as e:
                print(f"❌ Error procesando ocurrencia: {e}")
                stats["errors"] += 1
        
        conn.commit()
        
        print(f"✓ Ocurrencias importadas: {stats['inserted']}")
        if stats["duplicated"] > 0:
            print(f"⏭️  Duplicadas (gbif_occurrence_id ya existe): {stats['duplicated']}")
        if stats["errors"] > 0:
            print(f"❌ Errores: {stats['errors']}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error en importación de ocurrencias: {e}")
        return stats
    finally:
        conn.close()
