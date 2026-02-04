import requests
from .client import GBIF_URL

def get_vernacular_names_by_taxon_key(taxon_key: int):
    """
    Obtiene los nombres comunes de un taxón usando su taxon_key.
    """
    try:
        print(f"\nBuscando nombres comunes para taxon_key: {taxon_key}")

        res = requests.get(
            f"{GBIF_URL}/species/{taxon_key}/vernacularNames",
            timeout=10
        )
        res.raise_for_status()
        data = res.json()

        if "results" in data and data["results"]:
            vernacular_names = [
                {"vernacularName": name["vernacularName"], "language": name.get("language")}
                for name in data["results"]
                if "vernacularName" in name
            ]
            print(f"✓ Nombres comunes encontrados: {len(vernacular_names)}")
            return vernacular_names
        else:
            print("No se encontraron nombres comunes.")
            return []

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            print(f"No se encontró el taxón con la clave: {taxon_key}")
        else:
            print(f"Error HTTP: {http_err}")
    except Exception as e:
        print(f"Error al obtener nombres comunes: {e}")

    return []
