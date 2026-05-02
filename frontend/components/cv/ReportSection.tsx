import { AnalyzeResponse, Recommendation } from "@/lib/api";

interface ReportSectionProps {
  report: AnalyzeResponse;
}

const priorityLabel: Record<string, string> = {
  high: "Alta prioridad",
  medium: "Prioridad media",
  low: "Sugerencia",
};

function MatchScore({ score }: { score: number }) {
  const rounded = Math.round(score);
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-baseline gap-3">
        <span
          className="text-[#E8192C] font-light leading-none"
          style={{ fontSize: "clamp(4rem, 10vw, 7rem)" }}
        >
          {rounded}
          <span className="text-[#E8192C]/70 text-4xl align-top ml-1">%</span>
        </span>
        <span className="text-[#666] text-sm tracking-wide">
          de match con la vacante
        </span>
      </div>
      <div className="h-[2px] w-full bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-[#E8192C] to-[#C41425] transition-all duration-700"
          style={{ width: `${rounded}%` }}
        />
      </div>
    </div>
  );
}

function SkillsBlock({
  label,
  skills,
  tone,
}: {
  label: string;
  skills: string[];
  tone: "matched" | "missing" | "neutral";
}) {
  if (skills.length === 0) return null;

  const toneStyles = {
    matched: "text-emerald-300/90 border-emerald-400/20 bg-emerald-400/5",
    missing: "text-[#E8192C]/90 border-[#E8192C]/25 bg-[#E8192C]/5",
    neutral: "text-[#CBD5E1] border-white/10 bg-white/[0.03]",
  };

  return (
    <div className="flex flex-col gap-3">
      <p className="text-[#666] text-xs tracking-[0.2em] uppercase">{label}</p>
      <div className="flex flex-wrap gap-1.5">
        {skills.map((s) => (
          <span
            key={s}
            className={`px-2.5 py-1 rounded-md text-xs font-medium border ${toneStyles[tone]}`}
          >
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

function Strengths({ cv_analysis }: { cv_analysis: import("@/lib/api").CVAnalysis }) {
  const checks = [
    { label: "Incluye skills técnicas", ok: cv_analysis.extracted_skills.length > 0 },
    { label: "Incluye años de experiencia", ok: cv_analysis.experience_years != null },
    { label: "Incluye sección de educación", ok: cv_analysis.education.length > 0 },
    { label: "Incluye proyectos", ok: cv_analysis.has_projects },
    { label: "Área profesional identificada", ok: cv_analysis.area.label !== "No detectado" },
    { label: "Nivel de seniority claro", ok: cv_analysis.seniority.confidence >= 0.5 },
  ];

  const passing = checks.filter((c) => c.ok);
  if (passing.length === 0) return null;

  return (
    <section className="flex flex-col gap-4 pt-2 border-t border-white/5">
      <p className="text-[#E8192C] text-xs tracking-[0.3em] uppercase font-mono">
        Puntos fuertes
      </p>
      <ul className="flex flex-col gap-2">
        {passing.map((c) => (
          <li key={c.label} className="flex items-center gap-3">
            <span className="text-emerald-400 text-base leading-none">✓</span>
            <span className="text-[#D4D4D8] text-sm font-light">{c.label}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function ReportSection({ report }: ReportSectionProps) {
  const { cv_analysis, job_match, recommendations, narrative } = report;
  const paragraphs = narrative.split("\n\n").filter((p) => p.trim());

  return (
    <article className="flex flex-col gap-14 w-full pb-16 pt-4">
      {/* Encabezado */}
      <header className="flex flex-col gap-2">
        <p className="text-[#E8192C] text-xs tracking-[0.3em] uppercase font-mono">
          Análisis
        </p>
        <h2
          className="text-white font-light tracking-tight leading-tight"
          style={{ fontSize: "clamp(2rem, 4vw, 3rem)" }}
        >
          Esto es lo que encontramos en tu CV.
        </h2>
      </header>

      {/* Match score (solo si hay JD) */}
      {job_match.available && job_match.score != null && (
        <section>
          <MatchScore score={job_match.score} />
        </section>
      )}

      {/* Narrativa */}
      <section className="max-w-2xl">
        {paragraphs.map((p, i) => (
          <p
            key={i}
            className="text-[#D4D4D8] text-[17px] leading-[1.75] mb-5 last:mb-0 font-light"
          >
            {p}
          </p>
        ))}
      </section>

      {/* Puntos fuertes */}
      <Strengths cv_analysis={cv_analysis} />

      {/* Skills */}
      {(cv_analysis.extracted_skills.length > 0 || job_match.available) && (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-10 pt-2 border-t border-white/5">
          {job_match.available ? (
            <>
              <SkillsBlock
                label="Skills que tenés"
                skills={job_match.matched_skills}
                tone="matched"
              />
              <SkillsBlock
                label="Skills que te faltan"
                skills={job_match.missing_skills}
                tone="missing"
              />
            </>
          ) : (
            <div className="md:col-span-2">
              <SkillsBlock
                label="Skills detectadas en tu CV"
                skills={cv_analysis.extracted_skills}
                tone="neutral"
              />
            </div>
          )}
        </section>
      )}

      {/* Recomendaciones */}
      {recommendations.length > 0 && (
        <section className="flex flex-col gap-8 pt-2 border-t border-white/5">
          <div className="flex flex-col gap-1">
            <p className="text-[#E8192C] text-xs tracking-[0.3em] uppercase font-mono">
              Qué conviene ajustar
            </p>
            <h3
              className="text-white font-light tracking-tight"
              style={{ fontSize: "clamp(1.5rem, 2.5vw, 2rem)" }}
            >
              Recomendaciones concretas
            </h3>
          </div>

          <ol className="flex flex-col gap-8 max-w-2xl">
            {recommendations.map((rec: Recommendation, i) => (
              <li key={i} className="flex gap-5">
                <span className="text-[#E8192C] font-light text-2xl leading-none pt-1 tabular-nums shrink-0 w-8">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="flex flex-col gap-2 flex-1">
                  <span className="text-[#666] text-[11px] tracking-[0.2em] uppercase">
                    {priorityLabel[rec.priority] ?? rec.priority}
                  </span>
                  <p className="text-[#E4E4E7] text-[16px] leading-[1.7] font-light">
                    {rec.message}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}
    </article>
  );
}
