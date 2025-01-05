from datetime import timedelta

from pydantic import EmailStr, AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_host: str
    api_port: int

    email_address: EmailStr
    email_password: str
    smtp_server: str
    smtp_port: int

    api_site: AnyUrl
    my_site: AnyUrl

    min_wait_time_minutes: int  # Значение из `.env`

    @property
    def min_wait_time(self) -> timedelta:
        """Вычисляемое значение минимального времени ожидания."""
        return timedelta(minutes=self.min_wait_time_minutes)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()