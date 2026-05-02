"""
Parser de rangos de fechas en CVs.

Detecta rangos del tipo "June 2019 - current" o "Marzo 2022 - Diciembre 2024"
y calcula los años totales de experiencia, fusionando rangos solapados para
no contar doble cuando el candidato tuvo trabajos simultáneos.

Es una utilidad pura: no sabe nada de CVs, perfiles ni seniority. Recibe un
string, devuelve un float con los años. Esto la hace fácil de testear y
permite que la lógica de seniority viva en otra capa sin acoplarse al parsing.
"""

import re
from dataclasses import dataclass
from datetime import date


# Meses en inglés (full y abreviado) y español (full y abreviado).
# El parser los normaliza a número 1-12. Mantener todo en una sola tabla
# permite que agregar un idioma nuevo sea una sola entrada.
MONTHS = {
    # Inglés full
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    # Inglés abreviado
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
    # Español full
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12,
    # Español abreviado
    "ene": 1, "abr": 4, "ago": 8, "sept": 9, "set": 9, "dic": 12,
}

# Palabras que significan "hasta hoy". Se mapean a date.today().
PRESENT_WORDS = {
    "current", "present", "now", "today",
    "actualidad", "actual", "presente", "hoy",
}

# Separadores entre fecha inicio y fecha fin. Cubrimos guion, en-dash, em-dash,
# "to", "a", "hasta", "until". Algunos CVs usan tipografía elegante con –/—.
RANGE_SEPARATORS = r"\s*(?:-|–|—|to|a|hasta|until)\s+"

# Regex para "Mes Año": captura el mes (palabra) y el año (4 dígitos).
# Hacemos el mes opcional para tolerar rangos tipo "2019 - 2024".
MONTH_YEAR = r"(?:([A-Za-zÁÉÍÓÚáéíóúñÑ\.]+)\s+)?(\d{4})"

# Regex para "MM/YYYY" o "MM-YYYY" numérico.
NUMERIC_MONTH_YEAR = r"(\d{1,2})[/\-](\d{4})"

# Regex para "current / present / actualidad / etc"
PRESENT = rf"({'|'.join(PRESENT_WORDS)})"


@dataclass(frozen=True)
class DateRange:
    """Rango de fechas como pares (año, mes) inclusivos en ambos extremos."""
    start: date
    end: date

    def months(self) -> int:
        """Cantidad de meses entre start y end, inclusiva. Mínimo 1."""
        delta = (self.end.year - self.start.year) * 12 + (self.end.month - self.start.month)
        return max(delta + 1, 1)


# Patrón completo: "Mes Año - Mes Año" o "Mes Año - present".
# Usamos finditer en el texto crudo porque los rangos pueden estar en líneas
# diferentes y no queremos depender de cómo viene formateado.
RANGE_PATTERNS = [
    # "June 2019 - current" / "Marzo 2022 - Diciembre 2024" / "2019 - 2024"
    re.compile(
        rf"{MONTH_YEAR}{RANGE_SEPARATORS}(?:{PRESENT}|{MONTH_YEAR})",
        re.IGNORECASE,
    ),
    # "06/2019 - 12/2024" / "06/2019 - current"
    re.compile(
        rf"{NUMERIC_MONTH_YEAR}{RANGE_SEPARATORS}(?:{PRESENT}|{NUMERIC_MONTH_YEAR})",
        re.IGNORECASE,
    ),
]


def calculate_total_years(text: str) -> float | None:
    """
    Extrae todos los rangos de fechas del texto y devuelve los años totales
    de experiencia, fusionando rangos solapados.

    Devuelve None si no encuentra ningún rango parseable.
    """
    ranges = _extract_ranges(text)
    if not ranges:
        return None

    merged = _merge_overlapping(ranges)
    total_months = sum(r.months() for r in merged)
    return round(total_months / 12, 1)


def _extract_ranges(text: str) -> list[DateRange]:
    """Encuentra todos los rangos parseables en el texto."""
    ranges: list[DateRange] = []
    today = date.today()

    for match in RANGE_PATTERNS[0].finditer(text):
        start = _parse_word_date(match.group(1), match.group(2))
        end = _parse_end(match, word_end_groups=(4, 5), present_group=3, today=today)
        if start and end and start <= end:
            ranges.append(DateRange(start, end))

    for match in RANGE_PATTERNS[1].finditer(text):
        start = _parse_numeric_date(match.group(1), match.group(2))
        end = _parse_end_numeric(match, today=today)
        if start and end and start <= end:
            ranges.append(DateRange(start, end))

    return ranges


def _parse_word_date(month_word: str | None, year_str: str) -> date | None:
    """'June' + '2019' → date(2019, 6, 1). Mes ausente → enero."""
    year = int(year_str)
    if not _valid_year(year):
        return None
    if month_word is None:
        return date(year, 1, 1)
    month = MONTHS.get(month_word.lower().strip("."))
    if month is None:
        return None
    return date(year, month, 1)


def _parse_numeric_date(month_str: str, year_str: str) -> date | None:
    """'06' + '2019' → date(2019, 6, 1)."""
    month = int(month_str)
    year = int(year_str)
    if not (1 <= month <= 12) or not _valid_year(year):
        return None
    return date(year, month, 1)


def _parse_end(
    match: re.Match,
    word_end_groups: tuple[int, int],
    present_group: int,
    today: date,
) -> date | None:
    """End del rango: o bien 'current' o bien 'Mes Año'."""
    if match.group(present_group):
        return today
    month_g, year_g = word_end_groups
    if match.group(year_g):
        return _parse_word_date(match.group(month_g), match.group(year_g))
    return None


def _parse_end_numeric(match: re.Match, today: date) -> date | None:
    """Para el patrón numérico: grupo 3 es 'present', grupos 4-5 son MM/YYYY."""
    if match.group(3):
        return today
    if match.group(4) and match.group(5):
        return _parse_numeric_date(match.group(4), match.group(5))
    return None


def _valid_year(year: int) -> bool:
    """Filtra años absurdos (típicos errores de OCR como 1019 o 9999)."""
    return 1950 <= year <= date.today().year + 1


def _merge_overlapping(ranges: list[DateRange]) -> list[DateRange]:
    """
    Fusiona rangos que se solapan. Si el candidato trabajó en dos empresas
    al mismo tiempo, no contamos esos meses dos veces.
    """
    if not ranges:
        return []

    sorted_ranges = sorted(ranges, key=lambda r: r.start)
    merged = [sorted_ranges[0]]

    for current in sorted_ranges[1:]:
        last = merged[-1]
        if current.start <= last.end:
            merged[-1] = DateRange(last.start, max(last.end, current.end))
        else:
            merged.append(current)

    return merged
