from domain.entities import AnalysisReport
from domain.interfaces import ReportGeneratorInterface


class ReportGeneratorService(ReportGeneratorInterface):
    def generate(self, report: AnalysisReport) -> AnalysisReport:
        # Stub — se reemplaza en Fase 3 con lógica de reglas
        return report
