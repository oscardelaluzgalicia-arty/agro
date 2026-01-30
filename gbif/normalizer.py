def normalize_species(gbif_data: dict, otol_data: dict = None) -> dict:
    """
    Normaliza datos de GBIF, completando con datos de OpenTreeOfLife cuando sea necesario
    """
    if otol_data is None:
        otol_data = {}
    
    return {
        "taxonKey": gbif_data.get("key"),
        "scientific_name": gbif_data.get("scientificName"),
        "canonical_name": gbif_data.get("canonicalName"),
        "rank": gbif_data.get("rank"),
        "kingdom": gbif_data.get("kingdom"),
        # Usar datos de GBIF primero, luego OTOL como fallback
        "phylum": gbif_data.get("phylum") or otol_data.get("phylum"),
        "class_name": gbif_data.get("class") or otol_data.get("class"),
        "order_name": gbif_data.get("order") or otol_data.get("order"),
        "family": gbif_data.get("family") or otol_data.get("family"),
        "genus": gbif_data.get("genus") or otol_data.get("genus"),
        "species": gbif_data.get("species"),
        "taxonomic_status": gbif_data.get("taxonomicStatus")
    }
