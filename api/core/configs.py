from typing import Optional

from pydantic import BaseModel, PostgresDsn, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Налаштування застосунку."""

    name: str = Field(default="FastAPI Auth", description="Назва застосунку")
    version: str = Field(default="1.0.0", description="Версія застосунку")
    debug: bool = Field(default=False, description="Режим налагодження")
    environment: str = Field(default="production", description="Середовище виконання")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v


class RunConfig(BaseModel):
    host: str = Field(default="0.0.0.0", description="Хост сервера")
    port: int = Field(default=8000, description="Порт сервера", ge=1, le=65535)
    reload: bool = Field(default=False, description="Автоперезавантаження")


class DatabaseConfig(BaseModel):
    host: str = Field(default="localhost", description="Хост БД")
    port: int = Field(default=5432, description="Порт БД", ge=1, le=65535)
    name: str = Field(default="auth_db", description="Назва БД")
    user: str = Field(default="postgres", description="Користувач БД")
    password: str = Field(default="postgres", description="Пароль БД")

    echo: bool = Field(default=False, description="Логування SQL запитів")
    pool_size: int = Field(default=5, description="Розмір пулу з'єднань", ge=1)
    max_overflow: int = Field(default=10, description="Максимальна кількість додаткових з'єднань", ge=0)
    pool_timeout: int = Field(default=30, description="Таймаут очікування з'єднання", ge=1)
    pool_recycle: int = Field(default=3600, description="Час життя з'єднання в секундах", ge=60)

class JWTSettings(BaseSettings):
    secret_key: Optional[str] = Field(description="Секретний ключ для JWT", default=None)
    algorithm: str = Field(default="HS256", description="Алгоритм шифрування")
    access_token_expire_minutes: int = Field(
        default=15,
        description="Час життя access токена в хвилинах",
        ge=1
    )
    refresh_token_expire_days: int = Field(
        default=30,
        description="Час життя refresh токена в днях",
        ge=1
    )

    # @field_validator("secret_key")
    # @classmethod
    # def validate_secret_key(cls, v: str) -> str:
    #     print(v)
    #     if len(v) < 32:
    #         raise ValueError("Secret key must be at least 32 characters long")
    #     return v


class LogingSettings(BaseModel):
    level: str = Field(default="INFO", description="Рівень логування")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Формат логування"
    )
    file_path: Optional[str] = Field(default=None, description="Шлях до файлу логів")
    max_file_size: int = Field(default=10485760, description="Максимальний розмір файлу логів")
    backup_count: int = Field(default=5, description="Кількість backup файлів")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v_upper


class EmailSettings(BaseModel):
    smtp_host: Optional[str] = Field(default=None, description="SMTP хост")
    smtp_port: int = Field(default=587, description="SMTP порт", ge=1, le=65535)
    smtp_username: Optional[str] = Field(default=None, description="SMTP користувач")
    smtp_password: Optional[str] = Field(default=None, description="SMTP пароль")
    smtp_tls: bool = Field(default=True, description="Використовувати TLS")
    from_email: Optional[str] = Field(default=None, description="Email відправника")
    from_name: str = Field(default="FastAPI App", description="Ім'я відправника")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.template"),
        case_sensitive=False,
        extra="allow",
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    app: ApplicationSettings = ApplicationSettings()
    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig()
    jwt: JWTSettings = JWTSettings()
    loging: LogingSettings = LogingSettings()
    email: EmailSettings = EmailSettings()

    def get_database_url(self, async_driver: bool = True) -> str:
        """Генерує URL для підключення до бази даних."""

        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        return (f"{driver}://{self.db.user}:{self.db.password}" f"@{self.db.host}:{self.db.port}/{self.db.name}")

    def is_development(self) -> bool:
        """Перевіряє чи це середовище розробки."""
        return self.app.environment == "development"

    def is_production(self) -> bool:
        """Перевіряє чи це production середовище."""
        return self.app.environment == "production"

    def is_testing(self) -> bool:
        """Перевіряє чи це тестове середовище."""
        return self.app.environment == "testing"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Отримати екземпляр налаштувань (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings