import json
import uuid
from datetime import datetime

from fastapi.responses import RedirectResponse
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import EmailStr
from sqlmodel import Session

from app.db.confirmeduser.crud import create_confirmed_user, get_confirmed_user_email
from app.db.confirmeduser.model import ConfirmedUser
from app.db.database import get_session
from app.db.pendinguser.crud import (
    create_pending_user,
    get_pending_user,
    delete_pending_user_email,
)
from app.db.pendinguser.model import PendingUser
from app.utils.handle_existing import handle_existing_user
from config import settings
from send_email import email_sender
from .model import UserRegister

router = APIRouter()


@router.post("/")
async def add_user(user: UserRegister, session: Session = Depends(get_session)):
    # Проверка на созданного пользователя
    existing_confirmed_user = get_confirmed_user_email(session, user.email)

    if existing_confirmed_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с такой почтой уже зарегистрирован."
        )

    # Check if user is pending
    existing_pending_user = get_pending_user(session, user.email)
    if existing_pending_user:
        return await handle_existing_user(
            existing_pending_user,
            "register",
            f"user_id={user.user_id}&email={user.email}",
            session,
        )

    # Регистрируем нового пользователя
    new_user = PendingUser(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        email=user.email,
        key=str(uuid.uuid4()),
        key_expiry=datetime.utcnow() + settings.min_wait_time,
    )

    url = f"{settings.api_site}/register/validate/?email={new_user.email}&key={new_user.key}"

    await email_sender.send_email(
        subject="NextAuth Registration",
        body=f"Перейдите по ссылке, чтобы подтвердить свой профиль.\nСсылка: {url}",
        recipients=[user.email],
    )

    # Создаем нового пользователя в базе данных ожидающих подтверждения
    create_pending_user(session, new_user)

    return {"message": f"Письмо для создания аккаунта успешно отправлено на почту: {user.email}"}


@router.get("/validate/")
async def validate_key(
        email: EmailStr = Query(..., description="Email to validate"),
        key: str = Query(..., description="Key for validation"),
        session: Session = Depends(get_session),
):
    pending_user = get_pending_user(session, email)

    if not pending_user:
        #raise HTTPException(status_code=404, detail="Пользователь не найден.")
        return RedirectResponse(url=f"{settings.my_site}/register/fail", status_code=302)

    if pending_user.key != key or datetime.utcnow() > pending_user.key_expiry:
        #raise HTTPException(status_code=400, detail="Неверный или истекший ключ.")
        return RedirectResponse(url=f"{settings.my_site}/register/fail", status_code=302)

    # Перемещаем пользователя в созданных пользователей
    confirmed_user = ConfirmedUser(
        users_ids=json.dumps([pending_user.user_id]),
        first_name=pending_user.first_name,
        last_name=pending_user.last_name,
        middle_name=pending_user.middle_name,
        email=pending_user.email,
    )

    create_confirmed_user(session, confirmed_user)
    delete_pending_user_email(session, email)

    # URL для редиректа после успешной регистрации
    return RedirectResponse(url=f"{settings.my_site}/register/success", status_code=302)
