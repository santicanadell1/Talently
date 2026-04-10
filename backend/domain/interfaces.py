from abc import ABC, abstractmethod

from domain.entities import ExtractedProfile, JobMatch, AnalysisReport


class PDFExtractorInterface(ABC):
    @abstractmethod
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extrae texto plano de un PDF."""
        ...


class NERServiceInterface(ABC):
    @abstractmethod
    def extract_entities(self, text: str) -> dict:
        """Extrae entidades (skills, roles, orgs, educación) del texto."""
        ...


class ClassifierInterface(ABC):
    @abstractmethod
    def classify_seniority(self, text: str) -> dict:
        """Retorna {'label': str, 'confidence': float}."""
        ...

    @abstractmethod
    def classify_area(self, text: str) -> dict:
        """Retorna {'label': str, 'confidence': float}."""
        ...


class MatcherInterface(ABC):
    @abstractmethod
    def compute_match(self, profile: ExtractedProfile, job_description: str) -> JobMatch:
        """Calcula el match score entre el perfil y la job description."""
        ...


class ReportGeneratorInterface(ABC):
    @abstractmethod
    def generate(self, report: AnalysisReport) -> AnalysisReport:
        """Agrega recomendaciones al reporte en base al perfil y job match."""
        ...
