from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    hf_token: str

    # Modelos de HF Inference API (router.huggingface.co)
    ner_model: str = "Davlan/xlm-roberta-base-ner-hrl"
    zero_shot_model: str = "vicgalle/xlm-roberta-large-xnli-anli"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


settings = Settings()  # type: ignore[call-arg]
