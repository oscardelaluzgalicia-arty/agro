"""
Configuración y prompts para el traductor semántico
"""

def build_prompt(common_name: str) -> str:
    """
    Construye el prompt para OpenAI para obtener nombres científicos
    
    Args:
        common_name: Nombre común de la planta/fruta/verdura
        
    Returns:
        Prompt formateado para OpenAI
    """
    return f"""Devuelve exactamente los 3 nombres científicos más aceptados (binomial latino) 
de la fruta, verdura o planta conocida comúnmente como "{common_name}".

Formato de respuesta:
1. Nombre científico 1
2. Nombre científico 2
3. Nombre científico 3

- Solo devuelve los nombres científicos en formato binomial.
- Uno por línea, numerado.
- No agregues explicación.
- No agregues texto adicional.
- Si no estás seguro, omite ese nombre y continúa con los siguientes."""


# Configuración para validación GBIF
GBIF_CONFIDENCE_THRESHOLD = 80
GBIF_MATCH_ENDPOINT = "https://api.gbif.org/v1/species/match"
