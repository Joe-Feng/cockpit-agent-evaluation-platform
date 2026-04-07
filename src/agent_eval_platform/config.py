from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite+pysqlite:///:memory:"
    artifact_bucket: str = "agent-eval-artifacts"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    aws_region: str = "us-east-1"
    aws_s3_endpoint_url: str = "http://localhost:9000"
    alert_webhook_url: str | None = None
