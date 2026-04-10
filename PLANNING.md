# Analizador de CV con IA — Planificación del Proyecto

> Documento vivo. Se actualiza a medida que avanza el proyecto.
> Última actualización: 2026-04-09

---

## 1. Resumen del Proyecto

Aplicación web donde el usuario sube un CV en PDF y opcionalmente pega una descripción de trabajo (job description). Un agente de IA extrae información estructurada del CV, calcula un match score contra la vacante y genera recomendaciones concretas de mejora.

**App stateless:** no se guarda nada en base de datos. Cada sesión es independiente.

---

## 2. Arquitectura General

```
[Usuario]
    |
    | sube PDF + job description (opcional)
    v
[Frontend — Next.js]          <- Vercel
    |
    | POST /analyze (multipart form)
    v
[Backend — FastAPI]            <- Hugging Face Spaces
    |
    |-- PDF Extraction (pdfplumber)
    |-- Text Preprocessing
    |-- NER: extrae skills, experiencia, educación   <- HF Model
    |-- Profile Classification (seniority, área)     <- HF Model
    |-- Job Match Score (si hay JD)                  <- HF Model
    |-- Report Generator
    |
    | JSON con reporte estructurado
    v
[Frontend — Next.js]
    |
    | renderiza reporte
    v
[Usuario]
```

**¿Por qué esta separación?**
- Next.js en Vercel: deploy instantáneo, CDN global, ideal para frontend React.
- FastAPI en HF Spaces: el backend Python con ML vive donde están los modelos. HF Spaces tiene tier gratuito con CPU (y a veces GPU). Es temáticamente coherente para un portfolio de IA.

---

## 3. Stack Técnico

### Frontend
| Tecnología | Rol | Por qué |
|---|---|---|
| **Next.js 14** | Framework React full-stack | Aprende React + routing + API calls. Deploy nativo en Vercel. |
| **Tailwind CSS** | Estilos | Utilitario, rápido, no requiere experiencia previa en CSS. |
| **shadcn/ui** | Componentes UI | Componentes listos (botones, cards, progress bar) sobre Tailwind. |

### Backend
| Tecnología | Rol | Por qué |
|---|---|---|
| **Python 3.11** | Lenguaje | Ecosistema ML más maduro. |
| **FastAPI** | Framework API | Async nativo, docs automáticas (Swagger), Pydantic para validación. |
| **pdfplumber** | Extracción de texto PDF | Más preciso que PyPDF2, maneja layouts complejos. |
| **Hugging Face Inference API** | Modelos NLP | Tier gratuito, sin costo de infraestructura GPU. |
| **transformers / sentence-transformers** | Fallback local | Si los modelos en HF API no son suficientes. |

### Deploy
| Servicio | Qué hostea |
|---|---|
| **Vercel** | Frontend (Next.js) |
| **Hugging Face Spaces** | Backend (FastAPI) |

---

## 4. Módulos del Backend

### M1 — PDF Ingestion
- Recibe el archivo PDF via HTTP multipart
- Valida que sea un PDF y que no supere un tamaño máximo (ej. 5MB)
- Extrae el texto plano con `pdfplumber`
- Output: `string` con el texto del CV

### M2 — Text Preprocessing
- Limpieza básica: eliminar caracteres raros, normalizar espacios, saltos de línea
- Segmentación por secciones (Experiencia, Educación, Skills, etc.)
- Output: `dict` con secciones identificadas

### M3 — Entity Extraction (NER)
- Extrae entidades: skills técnicas, roles/cargos, empresas, años de experiencia, instituciones educativas
- Modelo candidato: `dslim/bert-base-NER` o `Jean-Baptiste/roberta-large-ner-english`
- Output: `dict` con entidades categorizadas

### M4 — Profile Classification
- Clasifica seniority (Junior / Mid / Senior / Lead)
- Clasifica área profesional (Backend Dev, Data Scientist, DevOps, etc.)
- Modelo candidato: Zero-shot con `facebook/bart-large-mnli`
- Output: `dict` con clasificaciones y scores de confianza

### M5 — Job Match Score
- Solo si el usuario pegó una job description
- Calcula similaridad semántica entre el perfil extraído y la JD
- Identifica skills presentes en la JD que faltan en el CV ("gaps")
- Modelo candidato: `sentence-transformers/all-MiniLM-L6-v2`
- Output: `float` (0-100) + lista de gaps

### M6 — Report Generator
- Consolida outputs de M3, M4, M5
- Genera sugerencias concretas (reglas + opcionalmente un LLM pequeño)
- Estructura el reporte final en JSON
- Output: `ReportSchema` (Pydantic model)

### M7 — API Layer
- `POST /analyze` — endpoint principal
- `GET /health` — healthcheck para HF Spaces
- CORS configurado para el dominio de Vercel
- Manejo de errores con códigos HTTP apropiados

---

## 5. Modelos de HF a Evaluar

> Esta sección se completa durante la Fase 2. Aquí están los candidatos.

| Tarea | Modelo Candidato | Notas |
|---|---|---|
| NER general | `dslim/bert-base-NER` | Rápido, liviano, bien documentado |
| NER más preciso | `Jean-Baptiste/roberta-large-ner-english` | Más pesado pero mejor precisión |
| Clasificación zero-shot | `facebook/bart-large-mnli` | Standard para zero-shot |
| Similaridad semántica | `sentence-transformers/all-MiniLM-L6-v2` | Rápido, ~80MB, excelente para semantic search |
| Generación de sugerencias | `google/flan-t5-base` | Pequeño, instruction-tuned, gratuito en HF API |

**Criterios de evaluación:**
- ¿Está disponible en HF Inference API gratuita?
- ¿Tiempo de respuesta aceptable (< 10s)?
- ¿Calidad de output suficiente para el caso de uso?
- ¿Cabe en 8GB VRAM para uso local si la API falla?

---

## 6. Schema del Reporte (JSON)

```json
{
  "cv_analysis": {
    "extracted_skills": ["Python", "FastAPI", "Docker"],
    "experience_years": 3,
    "roles": ["Backend Developer", "Data Engineer"],
    "education": ["Universidad X — Ingeniería en Sistemas"],
    "seniority": { "label": "Mid", "confidence": 0.82 },
    "area": { "label": "Backend Development", "confidence": 0.91 }
  },
  "job_match": {
    "score": 74.5,
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["Kubernetes", "Redis"],
    "available": true
  },
  "recommendations": [
    {
      "category": "skills_gap",
      "priority": "high",
      "message": "La vacante requiere experiencia con Kubernetes. Considera agregar proyectos con orquestación de contenedores."
    },
    {
      "category": "cv_structure",
      "priority": "medium",
      "message": "Tu sección de experiencia no menciona métricas de impacto. Agrega números concretos (ej. 'reduje tiempo de deploy en 40%')."
    }
  ]
}
```

---

## 7. Fases de Construcción

### Fase 0 — Setup (entorno + estructura)
- [ ] Crear repo en GitHub
- [ ] Estructura de carpetas del proyecto
- [ ] Entorno virtual Python + dependencias base
- [ ] Proyecto Next.js base
- [ ] Variables de entorno (.env.local y .env)

### Fase 1 — Backend Core (sin modelos)
- [ ] FastAPI skeleton con endpoint `/analyze` y `/health`
- [ ] M1: PDF Ingestion + extracción de texto con pdfplumber
- [ ] M7: API Layer básica (CORS, errores, validación de input)
- [ ] Test manual con Swagger UI

### Fase 2 — Integración de Modelos HF
- [ ] Evaluar modelos candidatos (ver sección 5)
- [ ] M3: Entity Extraction (NER)
- [ ] M4: Profile Classification (zero-shot)
- [ ] M5: Job Match Score (sentence transformers)
- [ ] Test de calidad de outputs

### Fase 3 — Generación de Reporte
- [ ] M2: Text Preprocessing
- [ ] M6: Report Generator con lógica de recomendaciones
- [ ] Definir reglas de negocio para sugerencias
- [ ] Output final en `ReportSchema`

### Fase 4 — Frontend
- [ ] Setup Next.js + Tailwind + shadcn/ui
- [ ] Página principal: upload de PDF + textarea para JD
- [ ] Llamada al backend (`/analyze`)
- [ ] UI del reporte: skills, score, recomendaciones
- [ ] Estados de loading y error

### Fase 5 — Deploy
- [ ] Deploy backend en HF Spaces
- [ ] Deploy frontend en Vercel
- [ ] Variables de entorno en producción
- [ ] Test end-to-end en producción

### Fase 6 — Polish (portfolio-ready)
- [ ] README atractivo con demo GIF
- [ ] Manejo de edge cases (PDFs escaneados, CVs en español/inglés)
- [ ] Optimización de tiempos de respuesta
- [ ] Responsive design

---

## 8. Decisiones Técnicas Pendientes

| Decisión | Opciones | Estado |
|---|---|---|
| ¿HF Inference API o modelos locales? | API gratuita vs local (3070 8GB) | Pendiente — evaluar en Fase 2 |
| ¿Sugerencias por reglas o LLM? | Reglas hardcodeadas vs flan-t5 | Pendiente — depende de calidad de outputs |
| ¿Soporte de CVs en español? | Solo inglés vs bilingüe | Pendiente — define alcance inicial |
| ¿Soporte de PDFs escaneados (imagen)? | OCR con pytesseract vs fuera de scope | Fuera de scope v1 |

---

## 9. Estructura de Carpetas (propuesta)

```
proyecto-cv/
├── frontend/               # Next.js
│   ├── app/
│   │   ├── page.tsx        # Página principal (upload)
│   │   ├── results/
│   │   │   └── page.tsx    # Página de resultados
│   │   └── layout.tsx
│   ├── components/
│   │   ├── CVUploader.tsx
│   │   ├── ReportCard.tsx
│   │   └── SkillBadge.tsx
│   └── lib/
│       └── api.ts          # Llamadas al backend
│
├── backend/                # FastAPI
│   ├── main.py             # Entry point
│   ├── routers/
│   │   └── analyze.py      # /analyze endpoint
│   ├── services/
│   │   ├── pdf_extractor.py
│   │   ├── ner_service.py
│   │   ├── classifier.py
│   │   ├── matcher.py
│   │   └── report_generator.py
│   ├── schemas/
│   │   └── report.py       # Pydantic models
│   └── requirements.txt
│
├── PLANNING.md             # Este archivo
└── README.md
```

---

## 10. Notas y Aprendizajes

> Esta sección se llena durante el desarrollo.

