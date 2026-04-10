from pydantic import BaseModel


class SenioritySchema(BaseModel):
    label: str
    confidence: float


class CVAnalysisSchema(BaseModel):
    extracted_skills: list[str]
    experience_years: int | None
    roles: list[str]
    education: list[str]
    seniority: SenioritySchema
    area: SenioritySchema  # misma estructura: label + confidence


class JobMatchSchema(BaseModel):
    available: bool
    score: float | None
    matched_skills: list[str]
    missing_skills: list[str]


class RecommendationSchema(BaseModel):
    category: str
    priority: str
    message: str


class AnalyzeResponseSchema(BaseModel):
    cv_analysis: CVAnalysisSchema
    job_match: JobMatchSchema
    recommendations: list[RecommendationSchema]
