from pydantic import EmailStr
from sqlmodel import Session, select, text

from app.db.confirmeduser.model import ConfirmedUser


def create_confirmed_user(session: Session, user: ConfirmedUser) -> ConfirmedUser:
    session.add(user)
    session.commit()
    session.refresh(user)  # Обновить объект для получения ID
    return user


def get_confirmed_user_userid(session: Session, user_id: int) -> ConfirmedUser:
    query = select(ConfirmedUser).where(text(f"json_extract(users_ids, '$') LIKE '%{user_id}%'"))
    return session.exec(query).first()


def get_all_confirmed_user_userid(session: Session, user_ids: list | int) -> list:
    # Убедимся, что user_ids - список целых чисел
    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    try:
        # Преобразуем элементы в список строк для SQL-запроса
        user_ids_str = ", ".join(map(str, user_ids))

        # Используем json_each для строгой проверки
        query = text(f"""
            SELECT confirmeduser.*
            FROM confirmeduser, json_each(confirmeduser.users_ids)
            WHERE json_each.value IN ({user_ids_str})
        """)

        # Выполняем запрос и получаем результат как список словарей
        result = session.execute(query).mappings().all()

        return result  # Результат уже JSON-совместимый

    except Exception as e:
        raise ValueError(f"Ошибка выполнения SQL-запроса: {e}")


def get_confirmed_user_email(session: Session, email: EmailStr) -> ConfirmedUser:
    return session.exec(select(ConfirmedUser).where(ConfirmedUser.email == email)).first()


def get_all_confirmed_users(session: Session):
    return session.exec(select(ConfirmedUser)).all()
