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

        # Paso 3: clasificar seniority y área
        seniority = self.classifier.classify_seniority(raw_text)
        area = self.classifier.classify_area(raw_text)

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
        )

        # Paso 5: calcular job match (solo si hay job description)
        if job_description:
            job_match = self.matcher.compute_match(profile, job_description)
        else:
            job_match = JobMatch(available=False)

        # Paso 6: generar reporte con recomendaciones
        report = AnalysisReport(profile=profile, job_match=job_match, recommendations=[])
        return self.report_generator.generate(report)
