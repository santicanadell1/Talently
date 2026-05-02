import re

from domain.entities import ExtractedProfile, JobMatch
from domain.interfaces import ClassifierInterface, MatcherInterface
from services.hf_client import hf_client
from services.ner_service import KNOWN_SKILLS, _skill_pattern
from core.config import settings

MIN_AREA_CONFIDENCE = 0.5

# Grupos de áreas afines. Áreas en el mismo grupo → sin penalización.
# Áreas en grupos distintos → penalización alta.
AREA_GROUPS: list[set[str]] = [
    {"Backend Development", "Frontend Development", "Full Stack Development", "Web Development"},
    {"Data Science", "Machine Learning Engineering"},
    {"DevOps"},
    {"Mobile Development"},
    {"QA / Testing"},
    {"Product Management", "UX/UI Design"},
]

AREA_MISMATCH_PENALTY_SAME_GROUP = 0.10   # Backend → Full Stack: cercanos
AREA_MISMATCH_PENALTY_DIFF_GROUP = 0.60   # Full Stack → Data Science: lejanos


class MatcherService(MatcherInterface):
    def __init__(self, classifier: ClassifierInterface):
        self.classifier = classifier

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
        #    - Si la JD tiene skills técnicas: 60% skills matcheadas + 40% semántica.
        #    - Si no tiene skills técnicas: 100% semántica. No inventamos skills_score
        #      neutral porque inflaría el match artificialmente.
        if jd_skills:
            skills_score = len(matched) / len(jd_skills)
            final_score = (0.6 * skills_score + 0.4 * semantic_score) * 100
        else:
            final_score = semantic_score * 100

        # 5. Penalización por área cuando CV y JD apuntan a roles claramente distintos.
        #    Solo aplica si ambas áreas se detectaron con confianza suficiente.
        final_score = self._apply_area_penalty(final_score, profile, job_description)

        return JobMatch(
            available=True,
            score=round(final_score, 1),
            matched_skills=matched,
            missing_skills=missing,
        )

    def _apply_area_penalty(
        self, score: float, profile: ExtractedProfile, job_description: str
    ) -> float:
        """
        Penaliza el score cuando el área del CV y la JD son distintas.
        Solo actúa si ambas áreas se detectaron con confianza >= MIN_AREA_CONFIDENCE.
        """
        cv_area = profile.area
        cv_confidence = profile.area_confidence or 0.0
        if not cv_area or cv_area == "Unknown" or cv_confidence < MIN_AREA_CONFIDENCE:
            return score

        jd_area_result = self.classifier.classify_area(job_description)
        jd_area = jd_area_result.get("label")
        jd_confidence = jd_area_result.get("confidence", 0.0)
        if not jd_area or jd_area == "Unknown" or jd_confidence < MIN_AREA_CONFIDENCE:
            return score

        if cv_area != jd_area:
            penalty = self._area_penalty(cv_area, jd_area)
            score = score * (1 - penalty)

        return score

    @staticmethod
    def _area_penalty(area_a: str, area_b: str) -> float:
        """Penalización según qué tan lejos están dos áreas entre sí."""
        for group in AREA_GROUPS:
            if area_a in group and area_b in group:
                return AREA_MISMATCH_PENALTY_SAME_GROUP
        return AREA_MISMATCH_PENALTY_DIFF_GROUP

    def _extract_skills_from_text(self, text: str) -> list[str]:
        """Misma lógica que NERService: busca skills conocidas en el texto."""
        found = []
        for skill in KNOWN_SKILLS:
            if re.search(_skill_pattern(skill), text, re.IGNORECASE):
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
