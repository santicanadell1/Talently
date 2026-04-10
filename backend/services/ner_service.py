from domain.interfaces import NERServiceInterface


class NERService(NERServiceInterface):
    def extract_entities(self, text: str) -> dict:
        # Stub — se reemplaza en Fase 2 con HF Inference API
        return {
            "skills": [],
            "roles": [],
            "organizations": [],
            "education": [],
            "experience_years": None,
        }
