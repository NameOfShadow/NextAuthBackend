import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.db.confirmeduser.model import ConfirmedUser
from app.db.pendinguser.model import PendingUser
from app.db.confirmeduser.crud import create_confirmed_user
from app.db.pendinguser.crud import create_pending_user
from app.db.database import get_session
from app.db.schemas import UserRegister, KeyCheck

router = APIRouter()

MIN_WAIT_TIME = timedelta(minutes=1)


@router.post("/register/")
def add_user(user: UserRegister, session: Session = Depends(get_session)):
    # Check if user is already confirmed
    existing_confirmed_user = session.exec(
        select(ConfirmedUser).where(ConfirmedUser.email == user.email)).first()
    if existing_confirmed_user:
        raise HTTPException(status_code=400, detail="Пользователь с такой почтой уже зарегистрирован.")

    # Check if user is pending
    existing_pending_user = session.exec(
        select(PendingUser).where(PendingUser.email == user.email)).first()
    if existing_pending_user:
        return handle_existing_pending_user(existing_pending_user, session, user)

    # Register new user
    new_user = PendingUser(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        email=user.email,
        key=str(uuid.uuid4()),
        key_expiry=datetime.utcnow() + MIN_WAIT_TIME
    )

    return create_pending_user(session, new_user)


def handle_existing_pending_user(existing_pending_user, session, user):
    now = datetime.utcnow()
    if now < existing_pending_user.key_expiry:
        remaining_time = (existing_pending_user.key_expiry - now).total_seconds()
        return {"message": f"Новый код для подтверждения можно будет отправить через {int(remaining_time)} секунд."}

    # Update key and expiry time if it's been more than 1 minute
    existing_pending_user.key = str(uuid.uuid4())
    existing_pending_user.key_expiry = now + MIN_WAIT_TIME
    session.add(existing_pending_user)
    session.commit()

    # Send new confirmation email
    # send_confirmation_email(user.email, existing_pending_user.key)

    return {"message": "Отправлен новый код подтверждения на почту."}


@router.post("/validate/")
def validate_key(data: KeyCheck, session: Session = Depends(get_session)):
    pending_user = session.exec(select(PendingUser).where(PendingUser.email == data.email)).first()

    if not pending_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    if pending_user.key != data.key or datetime.utcnow() > pending_user.key_expiry:
        raise HTTPException(status_code=400, detail="Неверный или истекший ключ.")

    # Move user from pending to confirmed
    confirmed_user = ConfirmedUser(
        users_ids=json.dumps([pending_user.user_id]),
        first_name=pending_user.first_name,
        last_name=pending_user.last_name,
        middle_name=pending_user.middle_name,
        email=pending_user.email
    )

    create_confirmed_user(session, confirmed_user)
    session.delete(pending_user)
    session.commit()

    return {"message": "Ключ успешно проверен. Пользователь зарегистрирован."}
