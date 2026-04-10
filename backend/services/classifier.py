from domain.interfaces import ClassifierInterface


class ClassifierService(ClassifierInterface):
    def classify_seniority(self, text: str) -> dict:
        # Stub — se reemplaza en Fase 2 con zero-shot HF
        return {"label": "Unknown", "confidence": 0.0}

    def classify_area(self, text: str) -> dict:
        # Stub — se reemplaza en Fase 2 con zero-shot HF
        return {"label": "Unknown", "confidence": 0.0}
