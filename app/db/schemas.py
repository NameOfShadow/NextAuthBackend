from pydantic import BaseModel, EmailStr, Field


# Базовая схема для пользователя (общие поля)
class UserBase(BaseModel):
    user_id: int
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)
    middle_name: str = Field(min_length=2, max_length=25)
    email: EmailStr


# Схема для создания пользователя (без id)
class UserRegister(UserBase):
    pass


class KeyCheck(BaseModel):
    email: EmailStr
    key: str
