from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PCI_", env_file=".env", extra="ignore")

    service_name: str = "pci-control-plane"
    environment: str = "local"
    database_url: str = Field(default="postgresql://pci:pci@postgres:5432/pci")
    nats_url: str = Field(default="nats://nats:4222")
    temporal_address: str = Field(default="temporal:7233")
    policy_bundle_version: str = "local-dev"
    enable_openapi: bool = True


settings = Settings()

