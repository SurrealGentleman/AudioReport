from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Service"
    app_version: str = "0.2.0"
    app_debug: bool = False
    log_level: str = "INFO"

    api_key: str

    whisper_model: str = "base"
    device_for_ai: str = "cpu"
    max_audio_file_size_mb: int = 100
    
    llama_model: str = "llama3"
    llama_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
