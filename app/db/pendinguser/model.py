from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


# Модель для ожидающего подтверждения пользователя
class PendingUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)
    middle_name: str = Field(min_length=2, max_length=25)
    email: EmailStr
    key: str = Field(default=None, nullable=True)
    key_expiry: datetime = Field(default=None, nullable=True)
