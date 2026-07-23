from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OLLAMA_API_KEY: str
    OLLAMA_HOST: str
    OLLAMA_AVAILABLE_MODELS: str
    OLLAMA_VISION_MODELS: str
    OLLAMA_MAX_TOKENS: int
    OLLAMA_REQUEST_TIMEOUT: int
    REFINEMENT_ITERATIONS: int
    DATA_FILE: str

    @property
    def models_list(self) -> list[str]:
        return [m.strip() for m in self.OLLAMA_AVAILABLE_MODELS.split(",") if m.strip()]

    @property
    def vision_models_list(self) -> list[str]:
        return [m.strip() for m in self.OLLAMA_VISION_MODELS.split(",") if m.strip()]

settings = Settings()