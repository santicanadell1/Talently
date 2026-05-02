from fastapi import HTTPException, UploadFile

from schemas.report import (
    AnalyzeResponseSchema,
    CVAnalysisSchema,
    JobMatchSchema,
    RecommendationSchema,
    SenioritySchema,
)
from use_cases.analyze_cv import AnalyzeCVUseCase
from domain.entities import AnalysisReport

MAX_PDF_SIZE_MB = 5


class AnalyzeController:
    def __init__(self, use_case: AnalyzeCVUseCase):
        self.use_case = use_case

    async def handle(
        self,
        file: UploadFile,
        job_description: str | None,
    ) -> AnalyzeResponseSchema:
        pdf_bytes = await self._validate_and_read(file)
        report = self.use_case.execute(pdf_bytes=pdf_bytes, job_description=job_description)
        return self._to_response(report)

    async def _validate_and_read(self, file: UploadFile) -> bytes:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

        pdf_bytes = await file.read()

        if len(pdf_bytes) > MAX_PDF_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"El PDF no puede superar {MAX_PDF_SIZE_MB}MB.",
            )

        return pdf_bytes

    def _to_response(self, report: AnalysisReport) -> AnalyzeResponseSchema:
        return AnalyzeResponseSchema(
            cv_analysis=CVAnalysisSchema(
                extracted_skills=report.profile.skills,
                experience_years=report.profile.experience_years,
                roles=report.profile.roles,
                education=report.profile.education,
                seniority=SenioritySchema(
                    label=report.profile.seniority or "Unknown",
                    confidence=report.profile.seniority_confidence or 0.0,
                ),
                area=SenioritySchema(
                    label=report.profile.area or "Unknown",
                    confidence=report.profile.area_confidence or 0.0,
                ),
            ),
            job_match=JobMatchSchema(
                available=report.job_match.available,
                score=report.job_match.score,
                matched_skills=report.job_match.matched_skills,
                missing_skills=report.job_match.missing_skills,
            ),
            recommendations=[
                RecommendationSchema(
                    category=r.category,
                    priority=r.priority,
                    message=r.message,
                )
                for r in report.recommendations
            ],
            narrative=report.narrative,
        )
