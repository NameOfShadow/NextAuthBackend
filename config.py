from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    email_address: str
    email_password: str
    smtp_server: str
    smtp_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
