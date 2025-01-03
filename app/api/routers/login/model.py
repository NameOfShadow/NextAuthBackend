from pydantic import BaseModel, EmailStr, Field


# Базовая схема для пользователя (общие поля)
class UserBase(BaseModel):
    user_id: int
    email: EmailStr


# Схема для создания пользователя (без id)
class UserLogin(UserBase):
    pass


class KeyCheck(BaseModel):
    user_id: int
    email: EmailStr
    key: str