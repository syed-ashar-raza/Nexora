from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nexora"
    environment: str = "development"
    api_key: str = ""
    rate_limit: int = 60
    rate_window_seconds: int = 60
    request_timeout_seconds: float = 30.0
    max_retries: int = 2
    retry_backoff_seconds: float = 0.1
    retry_max_backoff_seconds: float = 2.0
    retry_jitter_seconds: float = 0.05
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0
    routing_policy: str = "health_aware"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="NEXORA_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
