"""
Módulo para normalizar datos de observaciones de iNaturalist
Extrae solo los datos esenciales: ubicación y fecha
"""
from datetime import datetime

# Abreviaciones a estados mexicanos
ESTADO_MAP = {
    "AGS": "Aguascalientes", "BC": "Baja California", "BCS": "Baja California Sur",
    "CAMP": "Campeche", "CHIS": "Chiapas", "CHIH": "Chihuahua",
    "CDMX": "Ciudad de México", "COAH": "Coahuila", "COL": "Colima",
    "DGO": "Durango", "GTO": "Guanajuato", "GRO": "Guerrero",
    "HGO": "Hidalgo", "JAL": "Jalisco", "MEX": "Mexico",
    "MICH": "Michoacán", "MOR": "Morelos", "NAY": "Nayarit",
    "OAX": "Oaxaca", "PUE": "Puebla", "QRO": "Querétaro",
    "QROO": "Quintana Roo", "SLP": "San Luis Potosí", "SIN": "Sinaloa",
    "SON": "Sonora", "TAB": "Tabasco", "TAMPS": "Tamaulipas",
    "TLAX": "Tlaxcala", "VER": "Veracruz", "YUC": "Yucatán",
    "ZAC": "Zacatecas"
}

# Nombres de estados (variantes)
ESTADO_NAMES = {
    "Aguascalientes", "Baja California", "Baja California Sur",
    "Campeche", "Chiapas", "Chihuahua",
    "Ciudad de México", "Coahuila", "Colima",
    "Durango", "Guanajuato", "Guerrero",
    "Hidalgo", "Jalisco", "Mexico",
    "Michoacán", "Morelos", "Nayarit",
    "Oaxaca", "Puebla", "Querétaro",
    "Quintana Roo", "San Luis Potosí", "Sinaloa",
    "Sonora", "Tabasco", "Tamaulipas",
    "Tlaxcala", "Veracruz", "Yucatán",
    "Zacatecas"
}


def extract_state_from_place_guess(place_guess: str) -> str:
    """
    Extrae el estado mexicano de un place_guess de iNaturalist
    Ej: "Solidaridad, 47862 Ocotlán, Jal., México" -> "Jalisco"
    """
    if not place_guess:
        return "Unknown"
    
    # Buscar abreviaciones (Jal., Oax., etc.)
    parts = place_guess.split(",")
    for part in parts:
        part_clean = part.strip()
        
        # Remover puntos para comparación
        part_no_dot = part_clean.rstrip(".")
        
        # Buscar en mapa de abreviaciones (case-insensitive)
        for abbrev, full_name in ESTADO_MAP.items():
            if part_no_dot.upper() == abbrev:
                return full_name
        
        # Buscar nombre completo de estado
        for estado in ESTADO_NAMES:
            if part_clean.lower() == estado.lower():
                return estado
    
    # Si no encontró estado mexicano, usar la primera parte
    first_part = parts[0].strip() if parts else place_guess
    # Filtrar números de código postal
    if not first_part.isdigit():
        return first_part if first_part else "Unknown"
    
    return "Unknown"


def normalize_inaturalist_observation(obs: dict) -> dict:
    """
    Normaliza una observación de iNaturalist a formato compatible con occurrences
    SOLO extrae datos esenciales: ubicación y fecha
    
    Nota: iNaturalist puede no devolver coordenadas en search API,
    pero sí devuelve place_guess que se puede geocodificar después
    """
    try:
        # Ubicación
        latitude = obs.get("latitude")
        longitude = obs.get("longitude")
        place_guess = obs.get("place_guess", "Unknown")
        
        # Si no tiene coordenadas pero tiene ubicación válida, procesar igual
        if (not latitude or not longitude) and place_guess == "Unknown":
            return None
        
        # Extraer estado mexicano de place_guess
        state = extract_state_from_place_guess(place_guess)
        country = "Mexico"
        
        # Fecha
        observed_on = obs.get("observed_on")
        event_date = None
        year = month = day = None
        
        if observed_on:
            try:
                date_obj = datetime.fromisoformat(observed_on)
                event_date = date_obj.date()
                year = date_obj.year
                month = date_obj.month
                day = date_obj.day
            except:
                pass
        
        # Normalizar datos (con coordenadas opcionales por ahora)
        normalized = {
            # Ubicación (ESENCIAL para mapeo)
            "decimal_latitude": latitude,
            "decimal_longitude": longitude,
            "country": country,
            "state_province": state,
            "locality": place_guess,
            
            # Fecha (ESENCIAL para temporalidad)
            "event_date": event_date,
            "year": year,
            "month": month,
            "day": day,
            
            # Metadata
            "recorded_by": obs.get("user", {}).get("login", "Unknown") if isinstance(obs.get("user"), dict) else str(obs.get("user", "Unknown")),
            "basis_of_record": "OBSERVATION",
            "dataset_key": f"inaturalist_{obs.get('id')}",
            
            # Para agrupación de zonas (estado mexicano)
            "zone_key": f"MX|{state}",
            
            # Debug
            "has_coords": bool(latitude and longitude)
        }
        
        return normalized
        
    except Exception as e:
        print(f"⚠️ Error normalizando observación: {e}")
        return None


def normalize_inaturalist_observations(observations: list) -> list:
    """
    Normaliza múltiples observaciones de iNaturalist
    Filtra solo aquellas con ubicación válida
    """
    normalized_list = []
    with_coords = 0
    without_coords = 0
    
    for obs in observations:
        normalized = normalize_inaturalist_observation(obs)
        if normalized:
            normalized_list.append(normalized)
            if normalized.get("has_coords"):
                with_coords += 1
            else:
                without_coords += 1
    
    print(f"✓ {len(normalized_list)} observaciones válidas")
    print(f"  - Con coordenadas: {with_coords}")
    print(f"  - Solo ubicación: {without_coords}")
    return normalized_list
