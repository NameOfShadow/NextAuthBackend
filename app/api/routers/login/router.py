import json
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import EmailStr
from sqlmodel import Session

from app.api.routers.login.model import UserLogin
from app.db.confirmeduser.crud import get_confirmed_user_email
from app.db.database import get_session
from app.db.loginuser.crud import get_login_user_email, create_login_user, delete_login_user_email, \
    get_all_login_user_email
from app.db.loginuser.model import LoginUser
from app.utils.handle_existing import handle_existing_user
from config import settings
from send_email import email_sender

router = APIRouter()


@router.post("/")
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
    existing_login_user = next((existing_user for existing_user in existing_login_users if existing_user.user_id == user.user_id), None)

    if existing_login_user:
        # Если пользователь найден с таким user_id, обрабатываем его
        return await handle_existing_user(existing_login_user, "login", f"user_id={user.user_id}&email={user.email}", session)
    else:
        # Если пользователь не найден, создаем нового
        new_user = LoginUser(
            user_id=user.user_id,
            email=user.email,
            key=str(uuid.uuid4()),
            key_expiry=datetime.utcnow() + settings.min_wait_time
        )

        url = f"{settings.api_site}/login/validate/?user_id={new_user.user_id}&email={new_user.email}&key={new_user.key}"

        await email_sender.send_email(
            subject="NextAuth Login",
            body=f"Перейдите по ссылке, чтобы подтвердить свой профиль.\nСсылка: {url}",
            recipients=[user.email],
        )

        # Создаем нового пользователя в базе данных ожидающих подтверждения
        create_login_user(session, new_user)

        return {"message": f"Письмо с подтверждением нового входа в аккаунт успешно отправлено на почту: {user.email}"}


@router.get("/validate/")
async def validate_key(
    user_id: int = Query(..., description="User_ID to validate"),
    email: EmailStr = Query(..., description="Email to validate"),
    key: str = Query(..., description="Key to validation"),
    session: Session = Depends(get_session)
):
    login_user = get_login_user_email(session, email)
    confirmed_user = get_confirmed_user_email(session, email)

    if not login_user:
        raise HTTPException(status_code=404, detail="Пользователь не делал вход в акаунт с данной почтой.")

    if login_user.key != key or datetime.utcnow() > login_user.key_expiry:
        raise HTTPException(status_code=400, detail="Неверный или истекший ключ.")

    users_ids = json.loads(confirmed_user.users_ids)

    if user_id in users_ids:
        return {"message": "Такой пользователь с таким user_id уже есть в профиле"}
    else:
        # Добавляем user_id в список
        users_ids.append(user_id)
        confirmed_user.users_ids = json.dumps(users_ids)  # Преобразуем обратно в строку JSON
        session.add(confirmed_user)
        session.commit()

        # Удаляем пользователя из PendingUser, так как вход завершен
        delete_login_user_email(session, login_user.email)

        # Сделать ридерект на сайт после создания
        return {"message": "Вход успешен."}
