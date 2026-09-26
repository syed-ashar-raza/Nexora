from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nexora"
    environment: str = "development"
    api_key: str = ""
    rate_limit: int = 60
    rate_window_seconds: int = 60
    request_timeout_seconds: float = 30.0
    max_retries: int = 2
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="NEXORA_", env_file=".env", extra="ignore")

settings = Settings()
