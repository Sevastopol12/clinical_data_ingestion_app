from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    backend_base_url: str
    supabase_url: str
    supabase_anon_key: str
    request_upload: str
    request_record: str
    request_column_mapping: str
    dev_facility_id: UUID = UUID("00000000-0000-0000-0000-000000000000")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
