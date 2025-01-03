import json
from typing import List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


# Модель для подтвержденного пользователя
class ConfirmedUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    users_ids: str = Field(default="[]")
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)
    middle_name: str = Field(min_length=2, max_length=25)
    email: EmailStr

    @property
    def users_ids_list(self) -> List[int]:
        """Возвращает список пользователей из JSON-строки."""
        return json.loads(self.users_ids)

    @users_ids_list.setter
    def users_ids_list(self, value: List[int]):
        """Устанавливает список пользователей в JSON-строке."""
        self.users_ids = json.dumps(value)
