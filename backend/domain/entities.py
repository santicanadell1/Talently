from dataclasses import dataclass, field


@dataclass
class ExtractedProfile:
    raw_text: str
    sections: dict[str, str] = field(default_factory=dict)
    skills: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    organizations: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience_years: int | None = None
    seniority: str | None = None
    seniority_confidence: float | None = None
    area: str | None = None
    area_confidence: float | None = None


@dataclass
class JobMatch:
    available: bool
    score: float | None = None
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    category: str
    priority: str  # "high" | "medium" | "low"
    message: str


@dataclass
class AnalysisReport:
    profile: ExtractedProfile
    job_match: JobMatch
    recommendations: list[Recommendation]
    narrative: str = ""
