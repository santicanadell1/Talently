import time
from typing import Any

import httpx

from core.config import settings

HF_API_BASE = "https://router.huggingface.co/hf-inference/models"

# Cuando el modelo está en cold start, HF devuelve 503 con un estimated_time.
# Esperamos y reintentamos hasta un máximo de veces.
MAX_RETRIES = 3
COLD_START_WAIT = 20  # segundos


class HFClient:
    def __init__(self, token: str | None = None):
        self.token = token or settings.hf_token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def query(self, model: str, payload: dict[str, Any]) -> Any:
        """
        Llama a la HF Inference API para un modelo dado.
        Maneja cold starts con reintentos automáticos.
        """
        url = f"{HF_API_BASE}/{model}"

        for attempt in range(MAX_RETRIES):
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=self.headers, json=payload)

            # Caso feliz: respuesta OK
            if response.status_code == 200:
                return response.json()

            # Modelo cargándose (cold start)
            if response.status_code == 503:
                data = response.json()
                wait = min(data.get("estimated_time", COLD_START_WAIT), COLD_START_WAIT)
                time.sleep(wait)
                continue

            # Otro error: levantar excepción con el mensaje
            response.raise_for_status()

        raise RuntimeError(f"HF model {model} no respondió después de {MAX_RETRIES} intentos")


hf_client = HFClient()
