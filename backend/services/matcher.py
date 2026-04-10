from domain.entities import ExtractedProfile, JobMatch
from domain.interfaces import MatcherInterface


class MatcherService(MatcherInterface):
    def compute_match(self, profile: ExtractedProfile, job_description: str) -> JobMatch:
        # Stub — se reemplaza en Fase 2 con sentence-transformers
        return JobMatch(available=True, score=0.0, matched_skills=[], missing_skills=[])
