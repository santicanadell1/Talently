from domain.interfaces import ClassifierInterface
from services.hf_client import hf_client
from core.config import settings

SENIORITY_LABELS = ["Junior", "Mid", "Senior", "Lead"]

# Umbrales de seniority por años de experiencia. Tupla (min, max) inclusiva en
# min y exclusiva en max. Se evalúan en orden: el primero que matchea gana.
# Centralizado acá para que ajustar la política sea cambiar UNA línea.
# Lead no entra en la regla determinística: ser Lead es por responsabilidades,
# no por años. Si no hay años, el modelo zero-shot puede igual devolver Lead.
SENIORITY_THRESHOLDS = [
    ("Junior", 0, 2),
    ("Mid",    2, 5),
    ("Senior", 5, 999),
]

AREA_LABELS = [
    "Backend Development",
    "Frontend Development",
    "Full Stack Development",
    "Data Science",
    "Machine Learning Engineering",
    "DevOps",
    "Mobile Development",
    "QA / Testing",
    "Product Management",
    "UX/UI Design",
]


class ClassifierService(ClassifierInterface):
    def classify_seniority(self, text: str, experience_years: int | None) -> dict:
        """
        Clasifica seniority. Si tenemos años, regla determinística (confidence 1.0).
        Si no, caemos al modelo zero-shot que evalúa el texto crudo.
        """
        if experience_years is not None:
            return self._seniority_by_years(experience_years)
        return self._classify(text, SENIORITY_LABELS)

    def classify_area(self, text: str) -> dict:
        return self._classify(text, AREA_LABELS)

    @staticmethod
    def _seniority_by_years(years: int) -> dict:
        """Aplica la tabla de umbrales. Confidence 1.0 porque es determinístico."""
        for label, lo, hi in SENIORITY_THRESHOLDS:
            if lo <= years < hi:
                return {"label": label, "confidence": 1.0}
        # Fallback defensivo: no debería pasar con la tabla actual.
        return {"label": "Senior", "confidence": 1.0}

    def _classify(self, text: str, labels: list[str]) -> dict:
        """
        Llama al modelo zero-shot y retorna la label con mayor score.
        El modelo puede devolver dos formatos distintos:
        - Dict: {"labels": [...], "scores": [...]}
        - List: [{"label": "X", "score": 0.9}, ...]
        """
        try:
            result = hf_client.query(
                settings.zero_shot_model,
                {
                    "inputs": text[:2000],
                    "parameters": {"candidate_labels": labels},
                },
            )
        except Exception:
            return {"label": "Unknown", "confidence": 0.0}

        # Formato list
        if isinstance(result, list) and result:
            top = max(result, key=lambda x: x.get("score", 0))
            return {"label": top["label"], "confidence": float(top["score"])}

        # Formato dict
        if isinstance(result, dict) and "labels" in result:
            return {"label": result["labels"][0], "confidence": float(result["scores"][0])}

        return {"label": "Unknown", "confidence": 0.0}
