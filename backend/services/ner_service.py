import re

from domain.interfaces import NERServiceInterface
from services.hf_client import hf_client
from core.config import settings

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
    "Hugging Face", "LangChain",
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

# Regex para detectar años de experiencia en español e inglés
YEARS_REGEX = re.compile(
    r"(\d+)\s*(?:\+)?\s*(?:años?|years?|yr)\s*(?:de\s*experiencia|of\s*experience)?",
    re.IGNORECASE,
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
        """Busca skills conocidas en el texto con match case-insensitive."""
        found = []
        for skill in KNOWN_SKILLS:
            # \b = word boundary. Evita matchear "Java" dentro de "JavaScript".
            # re.escape para skills con caracteres especiales como "C++" o ".NET"
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                found.append(skill)
        return found

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
        """Busca menciones de años de experiencia y retorna el máximo."""
        matches = YEARS_REGEX.findall(text)
        if not matches:
            return None

        years = [int(m) for m in matches if m.isdigit()]
        # Filtramos valores absurdos (>50 años probablemente no sea experiencia)
        years = [y for y in years if 0 < y < 50]

        return max(years) if years else None
