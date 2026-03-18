from __future__ import annotations

from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StreamlitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_AGENT_UI_",
        extra="ignore",
        env_file=".env",
    )

    backend_base_url: str = Field(default="http://127.0.0.1:8000")
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    page_title: str = Field(default="db-agent")
    page_icon: str = Field(default="🗃️")
    debug: bool = False

    @cached_property
    def normalized_backend_base_url(self) -> str:
        return self.backend_base_url.rstrip("/")
