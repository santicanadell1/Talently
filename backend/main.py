from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analyze

app = FastAPI(
    title="Talently API",
    description="Analizador de CVs con IA",
    version="0.1.0",
)

# CORS: permite que el frontend en Vercel (u otro origen) llame a esta API.
# En producción reemplazar "*" por el dominio real de Vercel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)


@app.get("/health")
def health():
    return {"status": "ok"}
