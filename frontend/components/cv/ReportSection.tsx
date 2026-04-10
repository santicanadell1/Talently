import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AnalyzeResponse, Recommendation } from "@/lib/api";
import { SkillBadge } from "./SkillBadge";

interface ReportSectionProps {
  report: AnalyzeResponse;
}

const priorityLabel: Record<string, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

const priorityColor: Record<string, string> = {
  high: "text-[#B11623]",
  medium: "text-yellow-400",
  low: "text-[#CCCCCC]",
};

function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="flex gap-3 p-4 rounded-lg bg-[#111114] border border-[#3a3d4a]">
      <span className={`text-xs font-semibold mt-0.5 w-12 shrink-0 ${priorityColor[rec.priority]}`}>
        {priorityLabel[rec.priority]}
      </span>
      <p className="text-[#F0F0F0] text-sm leading-relaxed">{rec.message}</p>
    </div>
  );
}

export function ReportSection({ report }: ReportSectionProps) {
  const { cv_analysis, job_match, recommendations } = report;

  return (
    <div className="flex flex-col gap-6 w-full mt-10">
      <h2 className="text-[#F0F0F0] text-xl font-semibold">Resultado del análisis</h2>

      {/* Perfil */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[#292C37] border-[#3a3d4a]">
          <CardHeader className="pb-2">
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Seniority</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[#F0F0F0] text-2xl font-bold">{cv_analysis.seniority.label}</p>
            <p className="text-[#CCCCCC] text-xs mt-1">
              Confianza: {Math.round(cv_analysis.seniority.confidence * 100)}%
            </p>
          </CardContent>
        </Card>

        <Card className="bg-[#292C37] border-[#3a3d4a]">
          <CardHeader className="pb-2">
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Área</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[#F0F0F0] text-2xl font-bold">{cv_analysis.area.label}</p>
            <p className="text-[#CCCCCC] text-xs mt-1">
              Confianza: {Math.round(cv_analysis.area.confidence * 100)}%
            </p>
          </CardContent>
        </Card>

        <Card className="bg-[#292C37] border-[#3a3d4a]">
          <CardHeader className="pb-2">
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Experiencia</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[#F0F0F0] text-2xl font-bold">
              {cv_analysis.experience_years != null ? `${cv_analysis.experience_years} años` : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Match score */}
      {job_match.available && job_match.score != null && (
        <Card className="bg-[#292C37] border-[#3a3d4a]">
          <CardHeader className="pb-2">
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Match con la vacante</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex items-end gap-2">
              <span className="text-[#F0F0F0] text-4xl font-bold">{Math.round(job_match.score)}%</span>
            </div>
            <Progress value={job_match.score} className="h-2 bg-[#111114] [&>div]:bg-[#B11623]" />
            <div className="flex gap-6 mt-1">
              <div>
                <p className="text-[#CCCCCC] text-xs mb-2">Skills que tenés</p>
                <div className="flex flex-wrap gap-1">
                  {job_match.matched_skills.map((s) => (
                    <SkillBadge key={s} skill={s} variant="matched" />
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[#CCCCCC] text-xs mb-2">Skills que faltan</p>
                <div className="flex flex-wrap gap-1">
                  {job_match.missing_skills.map((s) => (
                    <SkillBadge key={s} skill={s} variant="missing" />
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Skills extraídas */}
      <Card className="bg-[#292C37] border-[#3a3d4a]">
        <CardHeader className="pb-2">
          <CardTitle className="text-[#CCCCCC] text-sm font-medium">Skills detectadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {cv_analysis.extracted_skills.length > 0
              ? cv_analysis.extracted_skills.map((s) => <SkillBadge key={s} skill={s} />)
              : <p className="text-[#CCCCCC] text-sm">No se detectaron skills.</p>
            }
          </div>
        </CardContent>
      </Card>

      {/* Recomendaciones */}
      {recommendations.length > 0 && (
        <Card className="bg-[#292C37] border-[#3a3d4a]">
          <CardHeader className="pb-2">
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Recomendaciones</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {recommendations.map((rec, i) => (
              <RecommendationCard key={i} rec={rec} />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
