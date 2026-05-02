"""
Normaliza errores típicos del OCR sobre el texto extraído de CVs.

Tesseract comete errores predecibles cuando el PDF es rasterizado:
caracteres similares (l/I, 0/O), separadores que se pierden ('React.js'
sale como 'Reactjs'), letras que se confunden con dígitos. En vez de
inflar la lista de skills con cada variante rota, normalizamos el texto
ANTES de buscar entidades.

Es una utilidad pura: recibe un string y devuelve un string. No conoce
CVs ni NER. La tabla de equivalencias se mantiene chica a propósito —
solo se agregan errores OBSERVADOS en CVs reales, no especulativos.
"""

import re

# Mapping de "patrón roto del OCR" → "forma canónica".
# La key es un regex con \b en los bordes (word boundary) para no romper
# palabras que contengan el patrón como substring (ej. "Reactjs" no debe
# matchear dentro de "Reactjsx"). Las keys se aplican en orden, pero como
# son palabras independientes el orden no importa hoy.
OCR_NORMALIZATIONS: dict[str, str] = {
    # React: el OCR pega "React" + "js" sin punto.
    r"\bReactjs\b": "React",
    r"\bReact\.js\b": "React",  # forma canónica que SÍ vamos a tener en KNOWN_SKILLS

    # MaterialUI: la I mayúscula muchas veces se lee como L minúscula.
    r"\bMaterialUl\b": "MaterialUI",
    r"\bMaterial Ul\b": "MaterialUI",
    r"\bMaterial UI\b": "MaterialUI",

    # Node.js: mismo patrón que React.
    r"\bNodejs\b": "Node.js",

    # Next.js
    r"\bNextjs\b": "Next.js",

    # Vue.js
    r"\bVuejs\b": "Vue",
}


def normalize(text: str) -> str:
    """Aplica todas las normalizaciones OCR conocidas sobre el texto."""
    for pattern, replacement in OCR_NORMALIZATIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
