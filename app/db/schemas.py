import uuid
from datetime import datetime, timedelta

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

#user = UserRegister(user_id=123,
#                    first_name="Damir",
#                    last_name="aas",
#                    middle_name="qas",
#                    email="aa@gmail.com",
#                    key=str(uuid.uuid4()),
#                    key_expiry=datetime.utcnow() + timedelta(minutes=1)
#)

#print(user.key_expiry.time().minute)
#print(datetime.utcnow().time().minute + 1)
#print(user.key_expiry.time().minute < datetime.utcnow().time().minute + 1.00001)
