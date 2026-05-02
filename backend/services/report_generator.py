import re

from domain.entities import AnalysisReport, Recommendation
from domain.interfaces import ReportGeneratorInterface

MIN_CONFIDENCE = 0.4


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
        report.narrative = self._build_narrative(report)
        return report

    # ---------- Narrativa ----------

    def _build_narrative(self, report: AnalysisReport) -> str:
        paragraphs: list[str] = []

        opening = self._opening_paragraph(report)
        if opening:
            paragraphs.append(opening)

        match_para = self._match_paragraph(report)
        if match_para:
            paragraphs.append(match_para)

        closing = self._closing_paragraph(report)
        if closing:
            paragraphs.append(closing)

        return "\n\n".join(paragraphs)

    def _opening_paragraph(self, report: AnalysisReport) -> str:
        profile = report.profile
        area = self._confident_label(profile.area, profile.area_confidence)
        seniority = self._confident_label(profile.seniority, profile.seniority_confidence)
        skills = profile.skills

        # Frase base
        if area and seniority:
            base = (
                f"Viendo tu CV llegamos a que tenés un perfil {seniority.lower()} "
                f"orientado a {area.lower()}"
            )
        elif area:
            base = f"Viendo tu CV llegamos a que tu perfil está orientado a {area.lower()}"
        elif seniority:
            base = f"Viendo tu CV identificamos un perfil {seniority.lower()}"
        else:
            base = "Viendo tu CV armamos un panorama general de tu perfil"

        # Skills destacadas (hasta 5)
        if skills:
            top = skills[:5]
            if len(top) == 1:
                skills_str = top[0]
            else:
                skills_str = ", ".join(top[:-1]) + f" y {top[-1]}"
            base += f", con manejo de {skills_str}"

        # Experiencia
        years = profile.experience_years
        if years:
            base += f". Detectamos alrededor de {years} año{'s' if years != 1 else ''} de experiencia"

        return base.rstrip(".") + "."

    def _match_paragraph(self, report: AnalysisReport) -> str:
        if not report.job_match.available or report.job_match.score is None:
            return ""

        score = report.job_match.score
        matched = report.job_match.matched_skills
        missing = report.job_match.missing_skills

        if score >= 75:
            tone = (
                f"Tu match con esta vacante es del {score}%, un encaje muy bueno: "
                "tu perfil se alinea con lo que buscan."
            )
        elif score >= 50:
            tone = (
                f"Tu match con esta vacante es del {score}%, una base decente "
                "aunque con margen para destacarte mejor."
            )
        else:
            tone = (
                f"Tu match con esta vacante es del {score}%, un encaje bajo: "
                "conviene reforzar varias áreas antes de aplicar."
            )

        if missing:
            top_missing = ", ".join(missing[:3])
            tone += f" Te faltan tecnologías clave como {top_missing}, que la vacante pide explícitamente."
        elif matched:
            tone += f" Ya tenés skills importantes que pide el puesto, como {', '.join(matched[:3])}."

        return tone

    def _closing_paragraph(self, report: AnalysisReport) -> str:
        profile = report.profile
        gaps: list[str] = []

        if profile.experience_years is None:
            gaps.append("no logramos identificar con claridad tus años de experiencia")

        seniority_confident = self._confident_label(profile.seniority, profile.seniority_confidence)
        if not seniority_confident:
            gaps.append("tu nivel de seniority no queda del todo claro")

        if len(profile.skills) < 5:
            gaps.append("la cantidad de skills técnicas que aparecen es baja")

        if not profile.education:
            gaps.append("no encontramos una sección de educación")

        if not gaps:
            return (
                "En general el CV comunica bien tu perfil. Abajo te dejamos algunos ajustes "
                "puntuales que pueden darle todavía más impacto."
            )

        if len(gaps) == 1:
            gaps_str = gaps[0]
        else:
            gaps_str = ", ".join(gaps[:-1]) + f", y {gaps[-1]}"

        return (
            f"Ahora bien, {gaps_str} — y eso puede jugarte en contra cuando un reclutador "
            "escanea tu CV en segundos. A continuación te dejamos lo que conviene ajustar."
        )

    def _confident_label(self, label: str | None, confidence: float | None) -> str | None:
        if not label or label == "Unknown":
            return None
        if confidence is None or confidence < MIN_CONFIDENCE:
            return None
        return label

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
        recs: list[Recommendation] = []
        profile = report.profile
        has_experience = profile.experience_years is not None and profile.experience_years > 0
        has_projects = self._has_projects_section(profile.raw_text)

        # Solo recomendamos métricas de impacto si el perfil tiene experiencia
        # laboral real. Para perfiles sin experiencia en tech, esta recomendación
        # no aplica y confunde al candidato.
        if has_experience:
            recs.append(Recommendation(
                category="cv_structure",
                priority="medium",
                message=(
                    "Agregá métricas de impacto a tus experiencias. "
                    "En lugar de 'optimicé el sistema', escribí 'reduje el tiempo de respuesta un 40%'. "
                    "Los números llaman la atención de los reclutadores."
                ),
            ))

        # Solo recomendamos agregar proyectos si no detectamos una sección de proyectos.
        if not has_projects:
            recs.append(Recommendation(
                category="cv_structure",
                priority="medium",
                message=(
                    "Incluí una sección de proyectos personales o contribuciones open source. "
                    "Es una excelente forma de demostrar iniciativa y pasión por el desarrollo."
                ),
            ))

        return recs

    @staticmethod
    def _has_projects_section(text: str) -> bool:
        """Detecta si el CV tiene una sección de proyectos."""
        if not text:
            return False
        pattern = re.compile(
            r"^(projects?|proyectos?|personal projects?|side projects?|portfolio)$",
            re.IGNORECASE | re.MULTILINE,
        )
        return bool(pattern.search(text))

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
