import reflex as rx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from reflex.constants import StateManagerMode


class _ReflexEnvironment(BaseSettings):
    redis_url: str | None = Field(default=None, validation_alias="REFLEX_REDIS_URL")
    auth_session_ttl_seconds: int = Field(
        default=86400, gt=0, validation_alias="AUTH_SESSION_TTL_SECONDS"
    )
    redis_token_expiration_override: int | None = Field(
        default=None, gt=0, validation_alias="REFLEX_REDIS_TOKEN_EXPIRATION"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def resolve_redis_state_ttl(
    auth_session_ttl_seconds: int,
    reflex_override_seconds: int | None = None,
) -> int:
    """Keep Reflex's Redis state alive at least as long as backend sessions."""
    if auth_session_ttl_seconds <= 0:
        raise ValueError("AUTH_SESSION_TTL_SECONDS must be positive")
    if reflex_override_seconds is not None:
        if reflex_override_seconds <= 0:
            raise ValueError("REFLEX_REDIS_TOKEN_EXPIRATION must be positive")
        if reflex_override_seconds < auth_session_ttl_seconds:
            raise ValueError(
                "REFLEX_REDIS_TOKEN_EXPIRATION must be at least "
                "AUTH_SESSION_TTL_SECONDS"
            )
        return reflex_override_seconds
    return auth_session_ttl_seconds


_environment = _ReflexEnvironment()
_redis_url = _environment.redis_url
_session_ttl = resolve_redis_state_ttl(
    _environment.auth_session_ttl_seconds,
    _environment.redis_token_expiration_override,
)

config = rx.Config(
    app_name="data_managment_system",
    redis_url=_redis_url,
    state_manager_mode=(
        StateManagerMode.REDIS if _redis_url else StateManagerMode.DISK
    ),
    # Reflex 0.9.8 uses redis_token_expiration for Redis-backed state/token TTL.
    # Keep persisted auth state alive for at least the backend session lifetime.
    redis_token_expiration=_session_ttl,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                accent_color="green",
                appearance="dark",
                has_background=True,
            ),
        ),
    ],
)
