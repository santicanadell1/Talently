import re

from domain.interfaces import NERServiceInterface
from services.hf_client import hf_client
from services.date_parser import calculate_total_years
from services.ocr_normalizer import normalize as normalize_ocr
from core.config import settings


# Patrones para detectar líneas de contacto (header del CV). Una línea es
# "de contacto" si matchea cualquiera de estos. Sirve para descartar skills
# que aparecen como texto suelto al lado de un email/URL/teléfono (típico
# falso positivo: "Github" como link al perfil, no como skill real).
CONTACT_PATTERNS = [
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),                  # email
    re.compile(r"https?://"),                                  # URL explícita
    re.compile(r"\b(?:www\.|linkedin\.com|github\.com)"),      # URLs comunes sin http
    re.compile(r"\(\d{3}\)\s*\d{3}[-\s]?\d{4}"),               # teléfono US
    re.compile(r"\+\d{1,3}\s?\d{3,}"),                         # teléfono internacional
]

# Cuántas líneas de "vecindad" miramos para considerar header. Si una skill
# solitaria aparece a ≤ N líneas de un dato de contacto, la descartamos.
CONTACT_NEIGHBORHOOD = 2

# Lista de skills técnicas conocidas. Se matchea contra el texto del CV.
# El matching es case-insensitive y requiere límites de palabra completos.
KNOWN_SKILLS = [
    # Lenguajes
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL", "HTML", "CSS", "Bash",
    # Frameworks / librerías
    "React", "Next.js", "Vue", "Angular", "Svelte", "Node.js", "Express",
    "FastAPI", "Django", "Flask", "Spring", "Spring Boot", "Laravel", "Rails",
    ".NET", "ASP.NET", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
    "Hugging Face", "LangChain", "jQuery", "MaterialUI", "Tailwind", "Bootstrap",
    "WordPress",
    # Bases de datos
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
    "DynamoDB", "Cassandra", "Oracle", "SQL Server",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI",
    "Lambda", "EC2", "S3", "CloudFormation",
    # Herramientas
    "Git", "GitHub", "GitLab", "Jira", "Figma", "Linux", "Unix",
    # Metodologías / conceptos
    "Agile", "Scrum", "Kanban", "REST", "GraphQL", "gRPC", "Microservices",
    "CI/CD", "TDD", "DDD", "Machine Learning", "Deep Learning", "NLP",
    "Computer Vision", "Data Science", "ETL", "Big Data",
]

# Regex para detectar años de experiencia en español e inglés ("3 años de experiencia")
YEARS_REGEX = re.compile(
    r"(\d+)\s*(?:\+)?\s*(?:años?|years?|yr)\s*(?:de\s*experiencia|of\s*experience)?",
    re.IGNORECASE,
)

# Headers que marcan el INICIO de la sección de experiencia laboral.
# Comparamos en lowercase contra cada línea del CV.
EXPERIENCE_HEADERS = (
    "work experience", "professional experience", "employment", "experience",
    "experiencia laboral", "experiencia profesional", "experiencia",
)

# Headers que marcan el FIN de esa sección (cualquier sección distinta).
# Si no encontramos ninguno, la sección llega hasta el final del texto.
NON_EXPERIENCE_HEADERS = (
    "education", "educación", "educacion", "formación", "formacion",
    "projects", "proyectos",
    "skills", "habilidades", "competencias",
    "certifications", "certificaciones",
    "languages", "idiomas",
    "courses", "cursos", "relevant courses",
    "career objective", "objective", "objetivo", "summary", "perfil",
    "awards", "premios", "publications", "publicaciones",
    "references", "referencias", "interests", "intereses",
)


class NERService(NERServiceInterface):
    def extract_entities(self, text: str) -> dict:
        return {
            "skills": self._extract_skills(text),
            "organizations": self._extract_organizations(text),
            "roles": [],  # Los roles los detectamos con zero-shot después
            "education": self._extract_education(text),
            "experience_years": self._extract_experience_years(text),
        }

    def _extract_skills(self, text: str) -> list[str]:
        """
        Busca skills conocidas en el texto. Pasos:
          1. Normalizar errores de OCR (Reactjs → React, MaterialUl → MaterialUI).
          2. Identificar líneas que son "header de contacto" para excluirlas.
          3. Para cada skill conocida, ver si aparece en líneas legítimas.
        """
        normalized = normalize_ocr(text)
        lines = normalized.split("\n")
        excluded_lines = self._contact_lines(lines)

        # Texto limpio: todas las líneas EXCEPTO las marcadas como contacto.
        usable_text = "\n".join(
            line for i, line in enumerate(lines) if i not in excluded_lines
        )

        found = []
        for skill in KNOWN_SKILLS:
            # \b = word boundary. Evita matchear "Java" dentro de "JavaScript".
            # re.escape para skills con caracteres especiales como "C++" o ".NET"
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, usable_text, re.IGNORECASE):
                found.append(skill)
        return found

    @staticmethod
    def _contact_lines(lines: list[str]) -> set[int]:
        """
        Devuelve el set de índices de líneas que pertenecen al "header de
        contacto". Una línea cuenta como contacto si:
          (a) ella misma matchea algún CONTACT_PATTERN, O
          (b) está a ≤ CONTACT_NEIGHBORHOOD líneas de una que sí matchea.

        Esto descarta nombres de redes ("Github", "Linkedin") que aparecen
        sueltos junto al email y al teléfono, sin descartar las mismas
        palabras cuando aparecen dentro de bullets de experiencia.
        """
        anchor_indices = [
            i for i, line in enumerate(lines)
            if any(p.search(line) for p in CONTACT_PATTERNS)
        ]
        if not anchor_indices:
            return set()

        excluded: set[int] = set()
        for anchor in anchor_indices:
            lo = max(0, anchor - CONTACT_NEIGHBORHOOD)
            hi = min(len(lines), anchor + CONTACT_NEIGHBORHOOD + 1)
            excluded.update(range(lo, hi))
        return excluded

    def _extract_organizations(self, text: str) -> list[str]:
        """Llama al modelo NER de HF para extraer organizaciones."""
        try:
            result = hf_client.query(settings.ner_model, {"inputs": text[:2000]})
        except Exception:
            return []

        # El modelo devuelve una lista de entidades con formato:
        # [{"entity_group": "ORG", "word": "...", "score": ...}, ...]
        # Filtramos: longitud mínima, score mínimo, y que empiece con mayúscula.
        orgs = set()
        if isinstance(result, list):
            for entity in result:
                if entity.get("entity_group") != "ORG":
                    continue
                word = entity.get("word", "").strip()
                score = entity.get("score", 0)
                if len(word) < 4 or score < 0.75:
                    continue
                if not word[0].isupper():
                    continue
                orgs.add(word)
        return sorted(orgs)

    def _extract_education(self, text: str) -> list[str]:
        """Detecta menciones de educación con keywords comunes."""
        education_keywords = [
            "universidad", "university", "ingeniería", "engineering",
            "licenciatura", "bachelor", "master", "phd", "doctorado",
            "instituto", "institute", "facultad", "college",
        ]

        lines = text.split("\n")
        education_lines = []
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 5 or len(line_clean) > 200:
                continue
            if any(kw in line_clean.lower() for kw in education_keywords):
                education_lines.append(line_clean)

        # Limitamos a 5 para no saturar el reporte
        return education_lines[:5]

    def _extract_experience_years(self, text: str) -> int | None:
        """
        Estima los años de experiencia. Estrategia en cascada:
          1. Parsear rangos de fechas en la sección de experiencia laboral.
          2. Fallback a buscar menciones explícitas tipo "3 años de experiencia".
          3. None si nada matcheó.
        """
        experience_section = self._extract_experience_section(text)
        years_from_dates = calculate_total_years(experience_section)
        if years_from_dates is not None and years_from_dates > 0:
            # El consumer espera int (entities["experience_years"]: int | None).
            # Redondeamos hacia arriba a partir de medio año para no subestimar.
            return int(round(years_from_dates))

        matches = YEARS_REGEX.findall(text)
        years = [int(m) for m in matches if m.isdigit() and 0 < int(m) < 50]
        return max(years) if years else None

    def _extract_experience_section(self, text: str) -> str:
        """
        Recorta el texto a la sección de experiencia laboral. Si no encuentra
        un header reconocido, devuelve el texto completo (mejor algo que nada).
        """
        lines = text.split("\n")
        start_idx = self._find_header_line(lines, EXPERIENCE_HEADERS)
        if start_idx is None:
            return text

        # Buscamos el próximo header de OTRA sección a partir de start_idx + 1.
        end_idx = self._find_header_line(
            lines, NON_EXPERIENCE_HEADERS, start_at=start_idx + 1
        )
        if end_idx is None:
            return "\n".join(lines[start_idx:])

        return "\n".join(lines[start_idx:end_idx])

    @staticmethod
    def _find_header_line(
        lines: list[str], headers: tuple[str, ...], start_at: int = 0
    ) -> int | None:
        """
        Devuelve el índice de la primera línea cuyo contenido (case-insensitive,
        sin espacios extra) coincide EXACTAMENTE con alguno de los headers.
        Pedimos match exacto para evitar falsos positivos (ej. "experiencia"
        dentro de un párrafo descriptivo).
        """
        for i in range(start_at, len(lines)):
            normalized = lines[i].strip().lower()
            if normalized in headers:
                return i
        return None
