from domain.entities import AnalysisReport, Recommendation
from domain.interfaces import ReportGeneratorInterface


class ReportGeneratorService(ReportGeneratorInterface):
    def generate(self, report: AnalysisReport) -> AnalysisReport:
        recommendations: list[Recommendation] = []

        if report.job_match.available:
            recommendations.extend(self._job_match_recommendations(report))
        else:
            recommendations.extend(self._general_recommendations(report))

        recommendations.extend(self._profile_recommendations(report))

        # Ordenamos: high > medium > low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        report.recommendations = recommendations[:6]  # máximo 6
        return report

    # ---------- Recomendaciones cuando hay job description ----------

    def _job_match_recommendations(self, report: AnalysisReport) -> list[Recommendation]:
        recs: list[Recommendation] = []
        missing = report.job_match.missing_skills
        score = report.job_match.score or 0

        if missing:
            top_missing = ", ".join(missing[:3])
            recs.append(Recommendation(
                category="skills_gap",
                priority="high",
                message=(
                    f"La vacante requiere {top_missing} y no lo detectamos en tu CV. "
                    "Si tenés experiencia con estas tecnologías, agregalas explícitamente. "
                    "Si no, considerá adquirir conocimientos básicos antes de aplicar."
                ),
            ))

        if score < 50:
            recs.append(Recommendation(
                category="match_score",
                priority="high",
                message=(
                    f"Tu match con esta vacante es del {score}%. Revisá si este puesto "
                    "se alinea con tu perfil o si necesitás reforzar áreas clave antes de aplicar."
                ),
            ))
        elif score < 75:
            recs.append(Recommendation(
                category="match_score",
                priority="medium",
                message=(
                    f"Tenés un match del {score}% con esta vacante. Con algunos ajustes "
                    "y destacando mejor tus skills relevantes podés aumentar tus chances."
                ),
            ))
        else:
            recs.append(Recommendation(
                category="match_score",
                priority="low",
                message=(
                    f"Excelente match del {score}% con esta vacante. Tu perfil encaja muy bien, "
                    "asegurate de destacar tus logros más relevantes en la carta de presentación."
                ),
            ))

        return recs

    # ---------- Recomendaciones sin job description ----------

    def _general_recommendations(self, report: AnalysisReport) -> list[Recommendation]:
        return [
            Recommendation(
                category="cv_structure",
                priority="medium",
                message=(
                    "Agregá métricas de impacto a tus experiencias. "
                    "En lugar de 'optimicé el sistema', escribí 'reduje el tiempo de respuesta un 40%'. "
                    "Los números llaman la atención de los reclutadores."
                ),
            ),
            Recommendation(
                category="cv_structure",
                priority="medium",
                message=(
                    "Incluí una sección de proyectos personales o contribuciones open source. "
                    "Es una excelente forma de demostrar iniciativa y pasión por el desarrollo."
                ),
            ),
        ]

    # ---------- Recomendaciones generales sobre el perfil ----------

    def _profile_recommendations(self, report: AnalysisReport) -> list[Recommendation]:
        recs: list[Recommendation] = []
        profile = report.profile

        if len(profile.skills) < 5:
            recs.append(Recommendation(
                category="skills_detail",
                priority="medium",
                message=(
                    f"Solo detectamos {len(profile.skills)} skills técnicas en tu CV. "
                    "Agregá una sección dedicada con tus tecnologías, frameworks y herramientas "
                    "para que sean más visibles."
                ),
            ))

        if profile.experience_years is None:
            recs.append(Recommendation(
                category="experience",
                priority="medium",
                message=(
                    "No pudimos detectar tus años de experiencia. Incluí fechas claras en cada puesto "
                    "(ej. 'Marzo 2022 - Presente') para que sea evidente tu trayectoria."
                ),
            ))

        if not profile.education:
            recs.append(Recommendation(
                category="education",
                priority="low",
                message=(
                    "No detectamos una sección de educación. Si tenés estudios formales o cursos "
                    "relevantes, agregalos aunque sean breves."
                ),
            ))

        if profile.seniority and profile.seniority_confidence and profile.seniority_confidence < 0.5:
            recs.append(Recommendation(
                category="clarity",
                priority="low",
                message=(
                    "Tu nivel de seniority no es claro en el CV. Usá un resumen al inicio del tipo "
                    "'Desarrollador Backend Semi Senior con 3 años de experiencia' para dar contexto inmediato."
                ),
            ))

        return recs
