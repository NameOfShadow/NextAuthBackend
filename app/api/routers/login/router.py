import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from app.api.routers.login.model import UserLogin, KeyCheck
from app.db.confirmeduser.crud import get_confirmed_user_email
from app.db.database import get_session
from app.db.loginuser.crud import get_login_user_email, create_login_user, delete_login_user_email, \
    get_all_login_user_email
from app.db.loginuser.model import LoginUser

router = APIRouter()
MIN_WAIT_TIME = timedelta(minutes=1)


@router.post("/login/")
async def login(user: UserLogin, session: Session = Depends(get_session)):
    # Ищем пользователя в базе данных с таким email
    confirmed_user = get_confirmed_user_email(session, user.email)

    if not confirmed_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    users_ids = json.loads(confirmed_user.users_ids)
    if user.user_id in users_ids:
        return {"message": "Такой пользователь с таким user_id уже есть в профиле"}

    # Получаем всех пользователей с данным email
    existing_login_users = get_all_login_user_email(session, user.email)

    # Ищем пользователя с таким же user_id среди существующих
    existing_login_user = next(
        (existing_user for existing_user in existing_login_users if existing_user.user_id == user.user_id), None)

    if existing_login_user:
        # Если пользователь найден с таким user_id, обрабатываем его
        return handle_existing_login_user(existing_login_user, session)
    else:
        # Если пользователь не найден, создаем нового
        new_user = LoginUser(
            user_id=user.user_id,
            email=user.email,
            key=str(uuid.uuid4()),
            key_expiry=datetime.utcnow() + MIN_WAIT_TIME
        )

        # Создаем нового пользователя в базе данных
        return create_login_user(session, new_user)


def handle_existing_login_user(existing_login_user, session):
    now = datetime.utcnow()

    # Проверяем, не истек ли срок действия кода
    if now < existing_login_user.key_expiry:
        remaining_time = (existing_login_user.key_expiry - now).total_seconds()
        return {"message": f"Новый код для подтверждения можно будет отправить через {int(remaining_time)} секунд."}

    # Если прошло больше времени, чем 1 минута, обновляем ключ и срок действия
    existing_login_user.key = str(uuid.uuid4())
    existing_login_user.key_expiry = now + MIN_WAIT_TIME  # MIN_WAIT_TIME должно быть определено ранее

    # Добавляем изменения в сессию и сохраняем их
    session.add(existing_login_user)
    session.commit()

    # Обновляем объект, чтобы получить актуальные данные
    session.refresh(existing_login_user)

    # Возвращаем новый ключ
    {existing_login_user.key}
    return {"message": f"Отправлен новый код подтверждения на почту!"}


@router.post("/validate_login/")
async def validate_login(data: KeyCheck, session: Session = Depends(get_session)):
    login_user = get_login_user_email(session, data.email)
    confirmed_user = get_confirmed_user_email(session, data.email)

    if not login_user:
        raise HTTPException(status_code=404, detail="Пользователь не делал вход в акаунт с данной почтой.")

    if login_user.key != data.key or datetime.utcnow() > login_user.key_expiry:
        raise HTTPException(status_code=400, detail="Неверный или истекший ключ.")

    users_ids = json.loads(confirmed_user.users_ids)

    if data.user_id in users_ids:
        return {"message": "Такой пользователь с таким user_id уже есть в профиле"}
    else:
        # Добавляем user_id в список
        users_ids.append(data.user_id)
        confirmed_user.users_ids = json.dumps(users_ids)  # Преобразуем обратно в строку JSON
        session.add(confirmed_user)
        session.commit()

        # Удаляем пользователя из PendingUser, так как вход завершен
        delete_login_user_email(session, login_user.email)

        return {"message": "Вход успешен."}
