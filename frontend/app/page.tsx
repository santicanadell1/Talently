"use client";

import { useState } from "react";
import Image from "next/image";
import { CVUploader } from "@/components/cv/CVUploader";
import { ReportSection } from "@/components/cv/ReportSection";
import { Textarea } from "@/components/ui/textarea";
import { analyzeCV, AnalyzeResponse } from "@/lib/api";
import { ArrowRight, Loader2 } from "lucide-react";

export default function Home() {
  const [file, setFile]                     = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading]               = useState(false);
  const [report, setReport]                 = useState<AnalyzeResponse | null>(null);
  const [error, setError]                   = useState<string | null>(null);

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
    <div className="min-h-screen bg-[#080808] text-[#F1F5F9] overflow-x-hidden">

      {/* Fondo — arco luminoso en forma de U */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">

        {/* Elipse grande con borde luminoso — esto crea el arco en U */}
        <div
          className="blob-red"
          style={{
            position: "absolute",
            bottom: "-70%",
            left: "50%",
            marginLeft: "-80vw",
            width: "160vw",
            height: "150vh",
            borderRadius: "50%",
            border: "2px solid rgba(232,25,44,0.5)",
            boxShadow:
              "0 0 120px 20px rgba(232,25,44,0.35), inset 0 0 120px 20px rgba(232,25,44,0.25)",
            filter: "blur(30px)",
          }}
        />

        {/* Segunda capa interior más intensa */}
        <div
          style={{
            position: "absolute",
            bottom: "-65%",
            left: "50%",
            marginLeft: "-70vw",
            width: "140vw",
            height: "130vh",
            borderRadius: "50%",
            border: "1px solid rgba(232,25,44,0.4)",
            boxShadow:
              "0 0 80px 10px rgba(232,25,44,0.25), inset 0 0 60px 10px rgba(232,25,44,0.15)",
            filter: "blur(20px)",
          }}
        />

        {/* Partículas */}
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          {[
            [120,80],[300,150],[500,60],[750,120],[950,90],[1150,180],[1300,70],
            [200,300],[420,250],[680,320],[880,280],[1100,350],[1350,300],
            [80,500],[350,480],[600,520],[820,490],[1050,510],[1280,470],
            [180,680],[440,650],[700,700],[930,660],[1200,690],
          ].map(([cx, cy], i) => (
            <circle key={i} cx={cx} cy={cy} r="1.5" fill="rgba(255,255,255,0.2)" />
          ))}
          {[
            [60,200],[260,400],[480,160],[820,380],[1020,200],[1180,420],[1380,160],
            [140,560],[380,600],[640,440],[900,580],[1140,440],[50,760],[320,740],
          ].map(([cx, cy], i) => (
            <circle key={`s${i}`} cx={cx} cy={cy} r="0.8" fill="rgba(255,255,255,0.12)" />
          ))}
        </svg>
      </div>

      {/* Nav */}
      <nav className="relative z-10 border-b border-white/5 px-8 py-4 bg-[#080808]/80 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Image
            src="/logo.png"
            alt="Talently"
            width={120}
            height={34}
            className="object-contain"
          />
          <span className="text-[#444] text-xs border border-white/8 rounded-full px-3 py-1 tracking-widest uppercase">
            Para developers
          </span>
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 flex flex-col">

        {/* Hero */}
        <section className="flex flex-col items-center text-center pt-28 pb-20 gap-10">
          <p className="animate-fade-up-1 text-[#444] text-xs tracking-[0.4em] uppercase font-mono">
            Análisis de CVs para perfiles tecnológicos.
          </p>

          <h1 className="animate-fade-up-2 font-sans leading-[1.08] tracking-[-0.01em] text-white"
            style={{ fontSize: "clamp(3rem, 7vw, 5.5rem)", fontWeight: 300, fontFamily: "var(--font-inter)" }}
          >
            Tu próximo rol tech empieza con un buen CV.
          </h1>

          <p className="animate-fade-up-3 text-[#444] text-base max-w-sm leading-relaxed font-light">
            Subí tu CV, pegá la descripción de la vacante y recibí
            recomendaciones concretas para destacar en el mercado tech.
          </p>
        </section>

        {/* Formulario */}
        <section className="animate-fade-up-4 flex flex-col gap-6 pb-20">

          {/* Divisor */}
          <div className="flex items-center gap-4 mb-2">
            <div className="h-px flex-1 bg-white/6" />
            <span className="text-[#444] text-xs tracking-widest uppercase">Comenzar</span>
            <div className="h-px flex-1 bg-white/6" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4" style={{ minHeight: "260px" }}>
            <CVUploader onFileSelect={setFile} selectedFile={file} />

            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <label className="text-[#888] text-xs tracking-widest uppercase">
                  Descripción de la vacante
                </label>
                <span className="text-[#444] text-xs tracking-widest uppercase">opcional</span>
              </div>
              <Textarea
                placeholder="Pegá acá la descripción del trabajo. Si la incluís, calculamos el match y los skills que te faltan."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="flex-1 h-full min-h-[220px] bg-[#111111] border-white/8 text-[#F1F5F9] placeholder:text-[#333] resize-none focus-visible:ring-1 focus-visible:ring-[#E8192C]/50 focus-visible:border-[#E8192C]/30 rounded-xl text-sm leading-relaxed transition-colors"
              />
            </div>
          </div>

          <div className="flex flex-col items-center gap-3 pt-2">
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="group flex items-center gap-2.5 px-8 py-3.5 rounded-xl font-semibold text-white text-sm
                bg-[#E8192C] hover:bg-[#C41425] transition-all duration-200
                disabled:opacity-30 disabled:cursor-not-allowed
                shadow-[0_0_40px_rgba(232,25,44,0.3)]"
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
              <p className="text-[#444] text-xs tracking-wide">Primero subí tu CV para continuar</p>
            )}
            {error && (
              <p className="text-[#E8192C] text-sm">{error}</p>
            )}
          </div>
        </section>

        {report && <ReportSection report={report} />}

      </main>

      <footer className="relative z-10 border-t border-white/5 py-8 px-6">
        <div className="max-w-4xl mx-auto text-center text-[#333] text-xs tracking-widest uppercase">
          Diseñado y desarrollado por{" "}
          <a
            href="https://www.linkedin.com/in/santiago-canadell-a15012297/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#555] hover:text-[#E8192C] transition-colors"
          >
            Santiago Canadell
          </a>
        </div>
      </footer>

    </div>
  );
}
