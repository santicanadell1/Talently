import re

from domain.entities import ExtractedProfile, JobMatch
from domain.interfaces import MatcherInterface
from services.hf_client import hf_client
from services.ner_service import KNOWN_SKILLS
from core.config import settings


class MatcherService(MatcherInterface):
    def compute_match(self, profile: ExtractedProfile, job_description: str) -> JobMatch:
        # 1. Extraer skills de la job description usando la misma lista
        jd_skills = self._extract_skills_from_text(job_description)

        # 2. Calcular qué skills tiene el perfil (intersección) y cuáles le faltan
        profile_skills_set = {s.lower() for s in profile.skills}
        matched = [s for s in jd_skills if s.lower() in profile_skills_set]
        missing = [s for s in jd_skills if s.lower() not in profile_skills_set]

        # 3. Calcular similaridad semántica entre el perfil y la JD
        semantic_score = self._semantic_similarity(profile.raw_text, job_description)

        # 4. Score final combinado:
        #    - 60% basado en skills matcheadas (peso concreto)
        #    - 40% basado en similaridad semántica (contexto general)
        if jd_skills:
            skills_score = len(matched) / len(jd_skills)
        else:
            skills_score = 0.5  # Neutral si no se detectaron skills en la JD

        final_score = (0.6 * skills_score + 0.4 * semantic_score) * 100

        return JobMatch(
            available=True,
            score=round(final_score, 1),
            matched_skills=matched,
            missing_skills=missing,
        )

    def _extract_skills_from_text(self, text: str) -> list[str]:
        """Misma lógica que NERService: busca skills conocidas en el texto."""
        found = []
        for skill in KNOWN_SKILLS:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                found.append(skill)
        return found

    def _semantic_similarity(self, cv_text: str, jd_text: str) -> float:
        """
        Usa sentence-transformers via HF API para calcular similaridad.
        El modelo acepta {source_sentence, sentences} y devuelve [score1, score2, ...]
        """
        try:
            result = hf_client.query(
                settings.embedding_model,
                {
                    "inputs": {
                        "source_sentence": jd_text[:1500],
                        "sentences": [cv_text[:1500]],
                    }
                },
            )
        except Exception:
            return 0.5  # Neutral ante fallo

        if isinstance(result, list) and result:
            # Sentence-transformers devuelve similaridad en [-1, 1], normalizamos a [0, 1]
            raw = float(result[0])
            return max(0.0, min(1.0, (raw + 1) / 2))

        return 0.5
