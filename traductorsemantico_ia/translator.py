"""
Módulo para traducción de nombres comunes a científicos usando OpenAI
"""
import os
import re
from typing import List, Optional
from openai import OpenAI
from .config import build_prompt


class SemanticTranslator:
    """Traductor de nombres comunes a científicos usando OpenAI"""
    
    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en .env")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Usando GPT-4o (más eficiente y preciso)
    
    def translate_to_scientific_names(self, common_name: str) -> List[str]:
        """
        Traduce un nombre común a nombres científicos usando OpenAI
        
        Args:
            common_name: Nombre común de la planta/fruta/verdura
            
        Returns:
            Lista de hasta 3 nombres científicos
            
        Raises:
            ValueError: Si hay error en la API de OpenAI
        """
        try:
            prompt = build_prompt(common_name)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en botánica y taxonomía. Tu tarea es proporcionar nombres científicos precisos y aceptados."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Bajo para respuestas más consistentes
                max_tokens=200
            )
            
            # Procesar la respuesta
            response_text = response.choices[0].message.content.strip()
            scientific_names = self._parse_scientific_names(response_text)
            
            return scientific_names
            
        except Exception as e:
            raise ValueError(f"Error al traducir con OpenAI: {str(e)}")
    
    def _parse_scientific_names(self, response_text: str) -> List[str]:
        """
        Parsea la respuesta de OpenAI para extraer nombres científicos
        
        Args:
            response_text: Texto de respuesta de OpenAI
            
        Returns:
            Lista de nombres científicos
        """
        lines = response_text.split('\n')
        scientific_names = []
        
        for line in lines:
            # Remover numeración y espacios
            line = re.sub(r'^\d+\.\s*', '', line).strip()
            
            # Validar que sea un nombre científico (2 o más palabras separadas por espacio)
            if line and len(line.split()) >= 2:
                # Capitalizar correctamente: Primera palabra con mayúscula, resto minúsculas
                parts = line.split()
                formatted_name = f"{parts[0].capitalize()} {' '.join(parts[1:]).lower()}"
                scientific_names.append(formatted_name)
        
        return scientific_names[:3]  # Retornar máximo 3


def get_translator() -> SemanticTranslator:
    """Factory function para obtener instancia del traductor"""
    return SemanticTranslator()
