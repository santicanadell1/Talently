"use client";

import { useState } from "react";
import { CVUploader } from "@/components/cv/CVUploader";
import { ReportSection } from "@/components/cv/ReportSection";
import { Textarea } from "@/components/ui/textarea";
import { analyzeCV, AnalyzeResponse } from "@/lib/api";

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
    <main className="min-h-screen bg-[#111114] px-4 py-12">
      <div className="mx-auto max-w-3xl flex flex-col gap-8">

        {/* Header */}
        <div className="flex flex-col gap-1">
          <h1 className="text-[#F0F0F0] text-3xl font-bold tracking-tight">
            Talently
          </h1>
          <p className="text-[#CCCCCC] text-base">
            Analizá tu CV con IA y descubrí cómo mejorar tu perfil profesional.
          </p>
        </div>

        {/* Formulario */}
        <div className="flex flex-col gap-4">
          <CVUploader onFileSelect={setFile} selectedFile={file} />

          <div className="flex flex-col gap-2">
            <label className="text-[#CCCCCC] text-sm">
              Descripción de la vacante{" "}
              <span className="text-[#CCCCCC]/60">(opcional)</span>
            </label>
            <Textarea
              placeholder="Pegá acá la descripción del trabajo al que querés aplicar..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={5}
              className="bg-[#292C37] border-[#3a3d4a] text-[#F0F0F0] placeholder:text-[#CCCCCC]/50 resize-none focus-visible:ring-[#B11623]"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full py-3 rounded-xl font-semibold text-[#F0F0F0] text-sm
              bg-[#B11623] hover:bg-[#9F111B] transition-colors
              disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? "Analizando..." : "Analizar CV →"}
          </button>

          {error && (
            <p className="text-[#B11623] text-sm text-center">{error}</p>
          )}
        </div>

        {/* Resultados */}
        {report && <ReportSection report={report} />}
      </div>
    </main>
  );
}
