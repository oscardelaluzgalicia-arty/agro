"""
Módulo para manejar la importación de zonas ecológicas
"""
from app.db import get_connection


def zone_exists(conn, country: str, state: str, biome: str):
    """Verifica si una zona ecológica ya existe"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_zone FROM ecological_zones 
            WHERE zone_name LIKE %s
            LIMIT 1
            """,
            (f"%{state}%",)
        )
        result = cur.fetchone()
        return result[0] if result else None


def insert_ecological_zone(conn, zone_name: str, biome_type: str, climate_type: str, description: str):
    """Inserta una nueva zona ecológica"""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO ecological_zones 
            (zone_name, biome_type, climate_type, description)
            VALUES (%s, %s, %s, %s)
            """,
            (zone_name, biome_type, climate_type, description)
        )
        return cur.lastrowid


def import_ecological_zones_with_species(zones_data_dict: dict, taxon_key: int, id_species: int) -> dict:
    """
    Importa zonas ecológicas y las asocia con la especie
    También importa las ocurrencias individuales
    
    zones_data_dict: {"zones": {...}, "occurrences": [...]}
    taxon_key: Taxon GBIF ID
    id_species: ID de la especie en la BD
    """
    from gbif.occurrences_handler import import_occurrences_batch
    from gbif.client import parse_occurrence
    
    conn = None
    stats = {
        "zones_inserted": 0,
        "zones_skipped": 0,
        "species_zones_linked": 0,
        "occurrences_inserted": 0,
        "occurrences_duplicated": 0,
        "occurrences_errors": 0,
        "errors": 0
    }
    
    try:
        conn = get_connection()
        
        print("\n" + "="*60)
        print("=== IMPORTANDO ZONAS ECOLÓGICAS ===")
        
        zones_data = zones_data_dict.get("zones", {})
        occurrences_list = zones_data_dict.get("occurrences", [])
        
        if not zones_data:
            print("⚠️ No hay datos de zonas para importar")
            return stats
        
        zone_mapping = {}  # Para mapear zone_key -> id_zone
        
        print(f"📍 Insertando {len(zones_data)} zonas ecológicas...")
        
        # Insertar zonas ecológicas
        for zone_key, zone_info in zones_data.items():
            try:
                country = zone_info.get("country", "Unknown")
                state = zone_info.get("state", "Unknown")
                zone_name = f"{country} - {state}"
                biome = zone_info.get("biome_type", "Unknown")
                climate = zone_info.get("climate_type", "Unknown")
                obs_count = zone_info.get("observation_count", 0)
                
                # Verificar si ya existe
                existing_id = zone_exists(conn, country, state, biome)
                
                if existing_id:
                    print(f"⏭️  Zona ya existe: {zone_name} (id: {existing_id})")
                    stats["zones_skipped"] += 1
                    zone_mapping[zone_key] = existing_id
                else:
                    # Insertar nueva zona
                    zone_id = insert_ecological_zone(
                        conn,
                        zone_name,
                        biome,
                        climate,
                        f"Observaciones: {obs_count}"
                    )
                    
                    print(f"✓ Zona insertada: {zone_name} (id: {zone_id})")
                    stats["zones_inserted"] += 1
                    zone_mapping[zone_key] = zone_id
                    
            except Exception as e:
                print(f"❌ Error importando zona {zone_key}: {str(e)}")
                stats["errors"] += 1
                continue
        
        # Asociar especies a zonas mediante species_zones
        print(f"\n🔗 Asociando especie a {len(zone_mapping)} zonas...")
        
        for zone_key, zone_id in zone_mapping.items():
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT IGNORE INTO species_zones (id_species, id_zone)
                        VALUES (%s, %s)
                        """,
                        (id_species, zone_id)
                    )
                    if cur.rowcount > 0:
                        stats["species_zones_linked"] += 1
                        
            except Exception as e:
                print(f"⚠️ Error asociando especie a zona: {e}")
                stats["errors"] += 1
        
        conn.commit()
        
        print(f"\n📊 RESUMEN DE ZONAS:")
        print(f"  Zonas insertadas: {stats['zones_inserted']}")
        print(f"  Zonas existentes: {stats['zones_skipped']}")
        print(f"  Especies asociadas: {stats['species_zones_linked']}")
        if stats['errors'] > 0:
            print(f"  ❌ Errores: {stats['errors']}")
        print("="*60)
        
        # Ahora importar ocurrencias parseadas
        if occurrences_list:
            print(f"\n📍 Parseando y importando {len(occurrences_list)} ocurrencias...")
            
            # Parsear todas las ocurrencias con la función del cliente
            parsed_occurrences = []
            for occ in occurrences_list:
                parsed = parse_occurrence(occ, id_species)
                parsed_occurrences.append(parsed)
            
            # Importar lote de ocurrencias parseadas
            occ_stats = import_occurrences_batch(parsed_occurrences)
            stats["occurrences_inserted"] = occ_stats["inserted"]
            stats["occurrences_duplicated"] = occ_stats.get("duplicated", 0)
            stats["occurrences_errors"] = occ_stats.get("errors", 0)
        
        return stats
        
    except Exception as e:
        print(f"❌ Error en importación de zonas: {str(e)}")
        import traceback
        traceback.print_exc()
        stats["errors"] += 1
        return stats
        
    finally:
        if conn:
            conn.close()
