import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AnalyzeResponse, Recommendation } from "@/lib/api";
import { SkillBadge } from "./SkillBadge";
import { TrendingUp, Briefcase, Clock, CheckCircle2, XCircle, Cpu, AlertCircle } from "lucide-react";

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

const priorityIcon: Record<string, React.ElementType> = {
  high: AlertCircle,
  medium: AlertCircle,
  low: AlertCircle,
};

function RecommendationCard({ rec }: { rec: Recommendation }) {
  const Icon = priorityIcon[rec.priority];
  return (
    <div className="flex gap-3 p-4 rounded-xl bg-[#111114] border border-[#3a3d4a]">
      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${priorityColor[rec.priority]}`} />
      <div className="flex flex-col gap-1">
        <span className={`text-xs font-semibold ${priorityColor[rec.priority]}`}>
          Prioridad {priorityLabel[rec.priority]}
        </span>
        <p className="text-[#F0F0F0] text-sm leading-relaxed">{rec.message}</p>
      </div>
    </div>
  );
}

export function ReportSection({ report }: ReportSectionProps) {
  const { cv_analysis, job_match, recommendations } = report;

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-[#292C37]" />
        <h2 className="text-[#CCCCCC] text-sm font-medium uppercase tracking-widest">
          Resultado del análisis
        </h2>
        <div className="h-px flex-1 bg-[#292C37]" />
      </div>

      {/* Cards de perfil */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[#1a1d27] border-[#3a3d4a]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#B11623]" />
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Seniority</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[#F0F0F0] text-2xl font-bold">{cv_analysis.seniority.label}</p>
            <p className="text-[#CCCCCC] text-xs mt-1">
              {Math.round(cv_analysis.seniority.confidence * 100)}% de confianza
            </p>
          </CardContent>
        </Card>

        <Card className="bg-[#1a1d27] border-[#3a3d4a]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <Briefcase className="w-4 h-4 text-[#B11623]" />
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Área</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-[#F0F0F0] text-2xl font-bold">{cv_analysis.area.label}</p>
            <p className="text-[#CCCCCC] text-xs mt-1">
              {Math.round(cv_analysis.area.confidence * 100)}% de confianza
            </p>
          </CardContent>
        </Card>

        <Card className="bg-[#1a1d27] border-[#3a3d4a]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <Clock className="w-4 h-4 text-[#B11623]" />
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
        <Card className="bg-[#1a1d27] border-[#3a3d4a]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <BarChart2Icon className="w-4 h-4 text-[#B11623]" />
            <CardTitle className="text-[#CCCCCC] text-sm font-medium">Match con la vacante</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex items-end gap-3">
              <span className="text-[#F0F0F0] text-4xl font-bold">{Math.round(job_match.score)}%</span>
              <span className="text-[#CCCCCC] text-sm mb-1">de compatibilidad</span>
            </div>
            <Progress value={job_match.score} className="h-1.5 bg-[#292C37] [&>div]:bg-[#B11623]" />
            <div className="grid grid-cols-2 gap-4 mt-1">
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                  <p className="text-[#CCCCCC] text-xs">Skills que tenés</p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {job_match.matched_skills.map((s) => (
                    <SkillBadge key={s} skill={s} variant="matched" />
                  ))}
                </div>
              </div>
              <div>
                <div className="flex items-center gap-1.5 mb-2">
                  <XCircle className="w-3.5 h-3.5 text-[#B11623]" />
                  <p className="text-[#CCCCCC] text-xs">Skills que faltan</p>
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
      <Card className="bg-[#1a1d27] border-[#3a3d4a]">
        <CardHeader className="pb-2 flex flex-row items-center gap-2">
          <Cpu className="w-4 h-4 text-[#B11623]" />
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
        <Card className="bg-[#1a1d27] border-[#3a3d4a]">
          <CardHeader className="pb-2 flex flex-row items-center gap-2">
            <AlertCircle className="w-4 h-4 text-[#B11623]" />
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

function BarChart2Icon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}
