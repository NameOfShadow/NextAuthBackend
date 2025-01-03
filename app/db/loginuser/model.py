from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


# Модель для пользователя подтверждающего вход
class LoginUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    email: EmailStr
    key: str = Field(default=None, nullable=True)
    key_expiry: datetime = Field(default=None, nullable=True)
