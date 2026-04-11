import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AnalyzeResponse, Recommendation } from "@/lib/api";
import { SkillBadge } from "./SkillBadge";
import { TrendingUp, Briefcase, Clock, CheckCircle2, XCircle, Cpu, AlertCircle, BarChart2 } from "lucide-react";

interface ReportSectionProps {
  report: AnalyzeResponse;
}

const priorityLabel: Record<string, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

const priorityColor: Record<string, string> = {
  high: "text-[#E8192C]",
  medium: "text-yellow-400",
  low: "text-[#94A3B8]",
};

function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="flex gap-3 p-4 rounded-xl bg-[#0E1117] border border-[#1E2433]">
      <AlertCircle className={`w-4 h-4 mt-0.5 shrink-0 ${priorityColor[rec.priority]}`} />
      <div className="flex flex-col gap-1">
        <span className={`text-xs font-semibold ${priorityColor[rec.priority]}`}>
          Prioridad {priorityLabel[rec.priority]}
        </span>
        <p className="text-[#F1F5F9] text-sm leading-relaxed">{rec.message}</p>
      </div>
    </div>
  );
}

export function ReportSection({ report }: ReportSectionProps) {
  const { cv_analysis, job_match, recommendations } = report;

  return (
    <div className="flex flex-col gap-6 w-full pb-8">
      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-[#1E2433]" />
        <h2 className="text-[#94A3B8] text-xs font-semibold uppercase tracking-widest">
          Resultado del análisis
        </h2>
        <div className="h-px flex-1 bg-[#1E2433]" />
      </div>

      {/* Cards de perfil */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            icon: TrendingUp,
            title: "Seniority",
            value: cv_analysis.seniority.label,
            sub: `${Math.round(cv_analysis.seniority.confidence * 100)}% de confianza`,
          },
          {
            icon: Briefcase,
            title: "Área",
            value: cv_analysis.area.label,
            sub: `${Math.round(cv_analysis.area.confidence * 100)}% de confianza`,
          },
          {
            icon: Clock,
            title: "Experiencia",
            value: cv_analysis.experience_years != null ? `${cv_analysis.experience_years} años` : "—",
            sub: null,
          },
        ].map(({ icon: Icon, title, value, sub }) => (
          <Card key={title} className="bg-[#161B27] border-[#1E2433]">
            <CardHeader className="pb-2 flex flex-row items-center gap-2">
              <Icon className="w-4 h-4 text-[#E8192C]" />
              <CardTitle className="text-[#94A3B8] text-sm font-medium">{title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#F1F5F9] text-2xl font-bold">{value}</p>
              {sub && <p className="text-[#94A3B8] text-xs mt-1">{sub}</p>}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Match score */}
      {job_match.available && job_match.score != null && (
        <Card className="bg-[#161B27] border-[#1E2433]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <BarChart2 className="w-4 h-4 text-[#E8192C]" />
            <CardTitle className="text-[#94A3B8] text-sm font-medium">Match con la vacante</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex items-end gap-2">
              <span className="text-[#F1F5F9] text-4xl font-bold">{Math.round(job_match.score)}%</span>
              <span className="text-[#94A3B8] text-sm mb-1">de compatibilidad</span>
            </div>
            <Progress value={job_match.score} className="h-1.5 bg-[#1E2433] [&>div]:bg-[#E8192C]" />
            <div className="grid grid-cols-2 gap-4 mt-1">
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <p className="text-[#94A3B8] text-xs">Skills que tenés</p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {job_match.matched_skills.map((s) => (
                    <SkillBadge key={s} skill={s} variant="matched" />
                  ))}
                </div>
              </div>
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <XCircle className="w-3.5 h-3.5 text-[#E8192C]" />
                  <p className="text-[#94A3B8] text-xs">Skills que faltan</p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {job_match.missing_skills.map((s) => (
                    <SkillBadge key={s} skill={s} variant="missing" />
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Skills */}
      <Card className="bg-[#161B27] border-[#1E2433]">
        <CardHeader className="pb-2 flex flex-row items-center gap-2">
          <Cpu className="w-4 h-4 text-[#E8192C]" />
          <CardTitle className="text-[#94A3B8] text-sm font-medium">Skills detectadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {cv_analysis.extracted_skills.length > 0
              ? cv_analysis.extracted_skills.map((s) => <SkillBadge key={s} skill={s} />)
              : <p className="text-[#94A3B8] text-sm">No se detectaron skills.</p>
            }
          </div>
        </CardContent>
      </Card>

      {/* Recomendaciones */}
      {recommendations.length > 0 && (
        <Card className="bg-[#161B27] border-[#1E2433]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <AlertCircle className="w-4 h-4 text-[#E8192C]" />
            <CardTitle className="text-[#94A3B8] text-sm font-medium">Recomendaciones</CardTitle>
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
