# Talently — Guía para Claude Code

## Qué es este proyecto

Analizador de CVs con IA. El usuario sube un PDF de CV y opcionalmente pega una job description. La app extrae información del CV, calcula un match score contra la vacante y genera recomendaciones concretas de mejora.

**App stateless**: no hay base de datos. Cada request es independiente.

---

## Cómo correr el proyecto localmente

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar HF_TOKEN
uvicorn main:app --reload
```

Swagger UI disponible en `http://localhost:8000/docs`

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

App disponible en `http://localhost:3000`

---

## Variables de entorno

### `backend/.env`

```
HF_TOKEN=hf_...   # Token de Hugging Face (obligatorio)
```

El `.env` nunca se commitea. El `.env.example` muestra la estructura.

### `frontend/.env.local` (si se necesita)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Por defecto apunta a `localhost:8000` si no se define.

---

## Arquitectura

```
frontend/          Next.js 14 App Router (SPA)
backend/
  main.py          Entry point FastAPI
  core/            Config (pydantic-settings)
  domain/          Entidades y contratos (interfaces)
  use_cases/       Orquestación del flujo principal
  api/
    routes/        Reciben HTTP, delegan al controller
    controllers/   Validan input, mapean a schema de respuesta
    dependencies/  Inyección de dependencias con FastAPI Depends()
  services/        Implementaciones concretas (HF, PDF, NER, etc.)
  schemas/         Pydantic models para request/response
```

### Flujo de una request

```
POST /analyze
  → AnalyzeController (valida PDF, mapea respuesta)
    → AnalyzeCVUseCase (orquesta)
      → PDFExtractor   (pdfplumber)
      → NERService     (regex skills + HF NER para orgs)
      → ClassifierService (zero-shot: seniority + área)
      → MatcherService    (skills gap + similaridad semántica)
      → ReportGeneratorService (reglas → recomendaciones)
```

---

## Modelos de Hugging Face en uso

| Tarea | Modelo |
|---|---|
| NER (organizaciones) | `Davlan/xlm-roberta-base-ner-hrl` |
| Zero-shot classification | `vicgalle/xlm-roberta-large-xnli-anli` |
| Similaridad semántica | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

**Endpoint:** `https://router.huggingface.co/hf-inference/models` (el viejo `api-inference.huggingface.co` está deprecado).

El cliente HF (`services/hf_client.py`) maneja cold starts con reintentos automáticos (503 → espera → reintenta, máximo 3 veces).

---

## Decisiones técnicas clave

- **NER híbrido**: regex para skills técnicas (lista `KNOWN_SKILLS` en `ner_service.py`) + modelo HF solo para organizaciones. Más confiable que NER puro para skills.
- **Score de match**: 60% skills matcheadas + 40% similaridad semántica. Balancea precisión concreta con fit general.
- **Recomendaciones por reglas**: sin LLM. Más predecible, sin alucinaciones, suficiente para el caso de uso.
- **Zero-shot model elegido**: `vicgalle/xlm-roberta-large-xnli-anli` — se probaron 4 modelos, este dio mejores resultados para seniority en español e inglés.
- **Clean architecture**: el use case no sabe nada de HTTP ni de HF. Los servicios implementan interfaces definidas en `domain/interfaces.py`.

---

## Stack frontend

- **Next.js 14** App Router (SPA — todo en `app/page.tsx`)
- **Tailwind CSS** + **shadcn/ui**
- **Outfit** (Google Fonts, weight 300) para el hero
- Fondo animado con blob CSS (`blob-breathe` keyframe en `globals.css`)
- Componentes custom: `CVUploader`, `ReportSection`, `SkillBadge`

---

## Deploy (pendiente)

- **Backend** → Hugging Face Spaces (Docker Space con FastAPI)
- **Frontend** → Vercel

---

## Lo que falta (próximas fases)

- Deploy backend en HF Spaces
- Deploy frontend en Vercel
- Responsive design / mobile
- Loading skeleton en el frontend
- README con demo GIF (portfolio-ready)
- Manejo de edge cases: PDFs escaneados, CVs muy cortos
