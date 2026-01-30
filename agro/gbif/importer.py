from app.db import get_connection

def species_exists(conn, taxon_key):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM species WHERE taxonKey=%s LIMIT 1",
            (taxon_key,)
        )
        return cur.fetchone() is not None

def insert_species(conn, data: dict):
    print("\n=== DATOS QUE SE VAN A INSERTAR ===")
    print(f"Datos completos: {data}")
    print(f"phylum a insertar: {data.get('phylum')}")
    print(f"class_name a insertar: {data.get('class_name')}")
    print(f"order_name a insertar: {data.get('order_name')}")
    print(f"family a insertar: {data.get('family')}")
    print(f"genus a insertar: {data.get('genus')}")
    print("===================================\n")
    
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO species
            (taxonKey, scientific_name, kingdom, phylum, class_name,
             order_name, family, genus, species, taxonomic_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data["taxonKey"],
                data["scientific_name"],
                data["kingdom"],
                data["phylum"],
                data["class_name"],
                data["order_name"],
                data["family"],
                data["genus"],
                data["species"],
                data["taxonomic_status"],
            )
        )




def import_species(data: dict) -> dict:
    conn = get_connection()
    try:
        if species_exists(conn, data["taxonKey"]):
            return {"status": "exists", "taxonKey": data["taxonKey"]}

        insert_species(conn, data)
        conn.commit()

        return {"status": "inserted", "taxonKey": data["taxonKey"]}
    finally:
        conn.close()


