from pydantic import BaseSettings


class Settings(BaseSettings):  # type: ignore[misc,valid-type]
    # Application settings
    app_name: str = "TwisterLab"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: str
    redis_url: str

    # Security settings
    secret_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
