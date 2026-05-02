import re

from domain.entities import AnalysisReport, ExtractedProfile, JobMatch
from domain.interfaces import (
    ClassifierInterface,
    MatcherInterface,
    NERServiceInterface,
    PDFExtractorInterface,
    ReportGeneratorInterface,
)


class AnalyzeCVUseCase:
    def __init__(
        self,
        pdf_extractor: PDFExtractorInterface,
        ner_service: NERServiceInterface,
        classifier: ClassifierInterface,
        matcher: MatcherInterface,
        report_generator: ReportGeneratorInterface,
    ):
        # Inyección de dependencias: el use case recibe los servicios desde afuera.
        # Esto permite swapear implementaciones sin tocar este archivo.
        self.pdf_extractor = pdf_extractor
        self.ner_service = ner_service
        self.classifier = classifier
        self.matcher = matcher
        self.report_generator = report_generator

    def execute(self, pdf_bytes: bytes, job_description: str | None) -> AnalysisReport:
        # Paso 1: extraer texto del PDF
        raw_text = self.pdf_extractor.extract_text(pdf_bytes)

        # Paso 2: extraer entidades con NER
        entities = self.ner_service.extract_entities(raw_text)

        # Paso 3: clasificar seniority y área.
        # Usamos un texto compacto (título + skills) para el área: el texto
        # completo del CV tiene bullets de trabajo que distraen al modelo
        # zero-shot y producen clasificaciones incorrectas (ej. "QA / Testing"
        # para alguien que menciona "QA sheets" en un bullet de experiencia).
        experience_years = entities.get("experience_years")
        classification_text = self._build_classification_text(raw_text, entities)
        seniority = self.classifier.classify_seniority(classification_text, experience_years)
        area = self.classifier.classify_area(classification_text)

        # Paso 4: armar el perfil
        profile = ExtractedProfile(
            raw_text=raw_text,
            skills=entities.get("skills", []),
            roles=entities.get("roles", []),
            organizations=entities.get("organizations", []),
            education=entities.get("education", []),
            experience_years=entities.get("experience_years"),
            seniority=seniority.get("label"),
            seniority_confidence=seniority.get("confidence"),
            area=area.get("label"),
            area_confidence=area.get("confidence"),
            has_projects=self._has_projects_section(raw_text),
        )

        # Paso 5: calcular job match (solo si hay job description)
        if job_description:
            job_match = self.matcher.compute_match(profile, job_description)
        else:
            job_match = JobMatch(available=False)

        # Paso 6: generar reporte con recomendaciones
        report = AnalysisReport(profile=profile, job_match=job_match, recommendations=[])
        return self.report_generator.generate(report)

    @staticmethod
    def _has_projects_section(text: str) -> bool:
        return bool(re.search(
            r"^(projects?|proyectos?|personal projects?|side projects?|portfolio)$",
            text, re.IGNORECASE | re.MULTILINE,
        ))

    @staticmethod
    def _build_classification_text(raw_text: str, entities: dict) -> str:
        """
        Arma un texto compacto con la información más relevante para clasificar
        área y seniority. Solo incluye las primeras dos líneas no vacías del CV
        (nombre + título declarado) más las skills detectadas.

        Limitamos a 2 líneas porque a partir de la tercera el CV suele tener
        datos de contacto (teléfono, email, LinkedIn) que no aportan semántica
        para la clasificación y pueden confundir al modelo.
        """
        non_empty = [l.strip() for l in raw_text.splitlines() if l.strip()]
        title_lines = "\n".join(non_empty[:2])
        skills = entities.get("skills", [])
        skills_str = ", ".join(skills) if skills else ""
        return f"{title_lines}\nSkills: {skills_str}".strip()
