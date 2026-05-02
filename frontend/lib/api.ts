const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SeniorityResult {
  label: string;
  confidence: number;
}

export interface CVAnalysis {
  extracted_skills: string[];
  experience_years: number | null;
  roles: string[];
  education: string[];
  seniority: SeniorityResult;
  area: SeniorityResult;
}

export interface JobMatch {
  available: boolean;
  score: number | null;
  matched_skills: string[];
  missing_skills: string[];
}

export interface Recommendation {
  category: string;
  priority: "high" | "medium" | "low";
  message: string;
}

export interface AnalyzeResponse {
  cv_analysis: CVAnalysis;
  job_match: JobMatch;
  recommendations: Recommendation[];
  narrative: string;
}

export async function analyzeCV(
  file: File,
  jobDescription?: string
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  if (jobDescription?.trim()) {
    form.append("job_description", jobDescription.trim());
  }

  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail ?? "Error al analizar el CV");
  }

  return res.json();
}
