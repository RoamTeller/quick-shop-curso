from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret: SecretStr = Field(min_length=32)
    frontend_base_url: AnyHttpUrl
    reset_minutes: int = Field(default=20, ge=1, le=60)
    bcrypt_rounds: int = Field(default=12, ge=4, le=16)
    email_provider: str = "smtp"
    smtp_host: str = ""
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: SecretStr = SecretStr("")
    smtp_starttls: bool = False
    email_from: str
    seed_admin_email: str
    seed_admin_password: SecretStr
    seed_client1_email: str
    seed_client1_password: SecretStr
    seed_client2_email: str
    seed_client2_password: SecretStr
    products_file: Path = Path(__file__).resolve().parents[2] / "docs" / "products-images.json"

@lru_cache
def get_settings() -> Settings:
    return Settings()
