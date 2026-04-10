from fastapi import APIRouter, Depends, File, Form, UploadFile

from api.controllers.analyze_controller import AnalyzeController
from api.dependencies import get_analyze_use_case
from schemas.report import AnalyzeResponseSchema
from use_cases.analyze_cv import AnalyzeCVUseCase

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponseSchema)
async def analyze_cv(
    file: UploadFile = File(..., description="CV en formato PDF"),
    job_description: str | None = Form(None, description="Descripción de la vacante (opcional)"),
    use_case: AnalyzeCVUseCase = Depends(get_analyze_use_case),
):
    controller = AnalyzeController(use_case)
    return await controller.handle(file=file, job_description=job_description)
