from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    backend_base_url: str
    request_upload: str
    request_record: str
    request_column_mapping: str
    request_rejection_artifact: str
    request_metric_period_summary: str
    request_metric_comorbidity: str
    request_metric_data_quality: str
    request_metric_patient_state: str
    request_metric_status: str
    login_path: str
    logout_path: str
    request_realtime_ws: str
    request_refresh: str
    realtime_backoff_base_seconds: float = 1.0
    realtime_backoff_max_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
