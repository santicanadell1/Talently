# Talently

**Demo en vivo:** https://talently-pi.vercel.app/

## Qué es

Talently es una aplicación que analiza currículums y ayuda a mejorarlos. Subís tu CV en PDF y, si querés, pegás la descripción de una vacante: la app te dice qué tan bien encaja tu perfil, qué te falta y te da recomendaciones concretas para mejorarlo.

## Qué hace

- Extrae texto de un CV en PDF (con fallback a OCR si el PDF es una imagen escaneada).
- Identifica skills técnicas, organizaciones, años de experiencia y estudios mediante un enfoque híbrido: reglas por regex para skills conocidas + un modelo de NER de Hugging Face para organizaciones.
- Clasifica seniority (Junior/Mid/Senior) y área profesional vía zero-shot classification.
- Si se pega una job description, calcula un match score (60% solapamiento de skills + 40% similaridad semántica) y detecta los gaps.
- Genera recomendaciones de mejora basadas en reglas, sin depender de un LLM generativo (evita alucinaciones).

## Arquitectura

App stateless — sin base de datos, cada request es independiente.

```
frontend/          Next.js 14 (App Router)
backend/
  main.py          Entry point FastAPI
  domain/          Entidades y contratos (interfaces)
  use_cases/        Orquestación del flujo principal
  api/
    routes/        Reciben HTTP, delegan al controller
    controllers/   Validan input, mapean respuesta
  services/        Implementaciones concretas (HF, PDF, OCR, NER, matching...)
  schemas/         Modelos Pydantic de request/response
```

El use case (`AnalyzeCVUseCase`) no conoce HTTP ni Hugging Face directamente: depende de interfaces definidas en `domain/interfaces.py`, e implementadas por los servicios concretos. Esto separa la lógica de negocio de los detalles de infraestructura y hace testeable cada capa por separado.

### Flujo de una request

```
POST /analyze
  → AnalyzeController (valida el PDF, mapea la respuesta)
    → AnalyzeCVUseCase (orquesta)
      → PDFExtractor + OCRNormalizer  (pdfplumber, con fallback a OCR)
      → NERService                    (regex de skills + HF NER para orgs)
      → ClassifierService             (zero-shot: seniority + área)
      → MatcherService                (skills gap + similaridad semántica)
      → ReportGeneratorService        (reglas → recomendaciones)
```

## Modelos de Hugging Face

| Tarea | Modelo |
|---|---|
| NER (organizaciones) | `Davlan/xlm-roberta-base-ner-hrl` |
| Zero-shot classification | `vicgalle/xlm-roberta-large-xnli-anli` |
| Similaridad semántica | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

El cliente HF maneja cold starts con reintentos automáticos (503 → espera → reintenta, hasta 3 veces).

## Decisiones técnicas

- **NER híbrido**: regex para skills técnicas conocidas + modelo HF solo para organizaciones. Más confiable que NER puro para este caso de uso.
- **Zero-shot para seniority**: se probaron varios modelos candidatos antes de quedarse con `vicgalle/xlm-roberta-large-xnli-anli`, por mejor desempeño en español e inglés.
- **Recomendaciones por reglas, no por LLM generativo**: más predecible, sin alucinaciones, y suficiente para el alcance del proyecto.
- **Clean Architecture**: separación estricta entre dominio, casos de uso y servicios de infraestructura.

## Stack

**Backend:** Python · FastAPI · pdfplumber · pytesseract (OCR) · Hugging Face Inference API
**Frontend:** Next.js 14 (App Router) · Tailwind CSS · shadcn/ui

## Cómo correrlo localmente

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar HF_TOKEN
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Swagger UI del backend disponible en `http://localhost:8000/docs`.
