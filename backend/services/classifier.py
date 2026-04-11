from domain.interfaces import ClassifierInterface
from services.hf_client import hf_client
from core.config import settings

SENIORITY_LABELS = ["Junior", "Mid", "Senior", "Lead"]

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
    def classify_seniority(self, text: str) -> dict:
        return self._classify(text, SENIORITY_LABELS)

    def classify_area(self, text: str) -> dict:
        return self._classify(text, AREA_LABELS)

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
