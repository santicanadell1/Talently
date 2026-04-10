from use_cases.analyze_cv import AnalyzeCVUseCase
from services.pdf_extractor import PDFExtractorService
from services.ner_service import NERService
from services.classifier import ClassifierService
from services.matcher import MatcherService
from services.report_generator import ReportGeneratorService


def get_analyze_use_case() -> AnalyzeCVUseCase:
    return AnalyzeCVUseCase(
        pdf_extractor=PDFExtractorService(),
        ner_service=NERService(),
        classifier=ClassifierService(),
        matcher=MatcherService(),
        report_generator=ReportGeneratorService(),
    )
