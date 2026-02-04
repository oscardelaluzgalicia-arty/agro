from app.db import get_connection
from gbif.vernacular import get_vernacular_names_by_taxon_key
import pymysql

def species_exists(conn, taxon_key: int):
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT id_species FROM species WHERE id_species = %s"
    cursor.execute(sql, (taxon_key,))
    result = cursor.fetchone()

    cursor.close()

    return result["id_species"] if result else None


def insert_species(conn, data: dict):
    print("USANDO INSERT_SPECIES NUEVO 🚀")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO species
            (taxonKey, scientific_name, kingdom, phylum, class_name,
             order_name, family, genus, species, taxonomic_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                id_species = LAST_INSERT_ID(id_species),
                scientific_name = VALUES(scientific_name)
            """,
            (
                data["taxonKey"],
                data["scientific_name"],
                data.get("kingdom"),
                data.get("phylum"),
                data.get("class_name"),
                data.get("order_name"),
                data.get("family"),
                data.get("genus"),
                data.get("species"),
                data.get("taxonomic_status"),
            )
        )

        conn.commit()
        return cur.lastrowid


def insert_vernacular_names(conn, species_id, vernacular_names):
    if not vernacular_names:
        return

    with conn.cursor() as cur:
        for name_info in vernacular_names:
            cur.execute(
                """
                INSERT INTO vernacular_names (id_species, language, common_name)
                VALUES (%s, %s, %s)
                """,
                (species_id, name_info['language'], name_info['vernacularName'])
            )

def import_species(data: dict) -> dict:
    conn = get_connection()
    try:
        species_id = species_exists(conn, data["taxonKey"])
        if species_id:
            return {"status": "exists", "id_species": species_id}

        species_id = insert_species(conn, data)
        
        vernacular_names = get_vernacular_names_by_taxon_key(data["taxonKey"])
        if vernacular_names:
            insert_vernacular_names(conn, species_id, vernacular_names)

        conn.commit()

        return {"status": "inserted", "id_species": species_id}
    finally:
        conn.close()
