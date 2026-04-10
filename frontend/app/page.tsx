"use client";

import { useState } from "react";
import { CVUploader } from "@/components/cv/CVUploader";
import { ReportSection } from "@/components/cv/ReportSection";
import { Textarea } from "@/components/ui/textarea";
import { analyzeCV, AnalyzeResponse } from "@/lib/api";
import { ArrowRight, Loader2, Sparkles, Target, BarChart2, Lightbulb, FileText } from "lucide-react";

const features = [
  { icon: FileText, label: "Extrae skills" },
  { icon: Target, label: "Detecta seniority" },
  { icon: BarChart2, label: "Calcula match" },
  { icon: Lightbulb, label: "Da recomendaciones" },
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await analyzeCV(file, jobDescription);
      setReport(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#111114]">

      {/* Nav */}
      <nav className="border-b border-[#292C37] px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#B11623] flex items-center justify-center">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <span className="text-[#F0F0F0] font-semibold text-lg tracking-tight">Talently</span>
          </div>
          <span className="text-[#CCCCCC] text-xs border border-[#292C37] rounded-full px-3 py-1">
            Beta
          </span>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-16 flex flex-col gap-16">

        {/* Hero */}
        <section className="flex flex-col items-center text-center gap-6">
          <span className="flex items-center gap-1.5 text-xs font-medium text-[#B11623] border border-[#B11623]/30 bg-[#B11623]/10 rounded-full px-4 py-1.5 tracking-wider uppercase">
            <Sparkles className="w-3 h-3" />
            Análisis de CVs con IA
          </span>

          <h1 className="text-5xl font-bold text-[#F0F0F0] leading-tight max-w-2xl tracking-tight">
            Descubrí exactamente{" "}
            <span className="text-[#B11623]">qué mejorar</span>{" "}
            en tu CV
          </h1>

          <p className="text-[#CCCCCC] text-lg max-w-xl leading-relaxed">
            Subí tu CV en PDF, pegá la descripción de la vacante que te interesa
            y recibí un análisis detallado con recomendaciones concretas.
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {features.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 bg-[#292C37] border border-[#3a3d4a] rounded-full px-4 py-2 text-sm text-[#CCCCCC]"
              >
                <Icon className="w-3.5 h-3.5 text-[#B11623]" />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Formulario */}
        <section className="flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4" style={{ minHeight: "260px" }}>
            <CVUploader onFileSelect={setFile} selectedFile={file} />

            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <label className="text-[#F0F0F0] text-sm font-medium">
                  Descripción de la vacante
                </label>
                <span className="text-[#CCCCCC]/60 text-xs border border-[#3a3d4a] rounded-full px-2 py-0.5">
                  opcional
                </span>
              </div>
              <Textarea
                placeholder="Pegá acá la descripción del trabajo al que querés aplicar. Si la incluís, calculamos el porcentaje de match y los skills que te faltan."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="flex-1 h-full min-h-[220px] bg-[#1a1d27] border-[#3a3d4a] text-[#F0F0F0] placeholder:text-[#CCCCCC]/40 resize-none focus-visible:ring-[#B11623] focus-visible:ring-1 focus-visible:border-[#B11623] rounded-2xl text-sm leading-relaxed"
              />
            </div>
          </div>

          <div className="flex flex-col items-center gap-3">
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="group flex items-center gap-2 px-8 py-3.5 rounded-xl font-semibold text-[#F0F0F0] text-sm
                bg-[#B11623] hover:bg-[#9F111B] transition-all duration-200
                disabled:opacity-40 disabled:cursor-not-allowed
                shadow-lg shadow-[#B11623]/20 hover:shadow-[#B11623]/30"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analizando...
                </>
              ) : (
                <>
                  Analizar CV
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>

            {!file && (
              <p className="text-[#CCCCCC]/50 text-xs">Primero subí tu CV para continuar</p>
            )}

            {error && (
              <p className="text-[#B11623] text-sm">{error}</p>
            )}
          </div>
        </section>

        {report && <ReportSection report={report} />}

      </main>

      <footer className="border-t border-[#292C37] mt-16 py-8 px-6">
        <div className="max-w-5xl mx-auto text-center text-[#CCCCCC]/40 text-xs">
          Talently · Analizador de CVs con IA
        </div>
      </footer>

    </div>
  );
}
