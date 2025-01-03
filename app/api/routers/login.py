import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.db.confirmeduser.model import ConfirmedUser
from app.db.pendinguser.model import PendingUser
from app.db.database import get_session


router = APIRouter()
CODE_LIFETIME = timedelta(minutes=1)


def send_code_for_existing_user(user_id: int, email: str, session: Session):
    # Ищем подтвержденного пользователя с таким email
    confirmed_user = session.exec(select(ConfirmedUser).where(ConfirmedUser.email == email)).first()

    if not confirmed_user:
        raise HTTPException(status_code=404, detail="Пользователь с такой почтой не найден.")

    # Проверяем, есть ли user_id в списке users_ids этого пользователя
    if user_id in confirmed_user.users_ids_list:
        # Если user_id найден в списке, генерируем и отправляем код для входа
        new_pending_user = PendingUser(
            email=email,
            user_id=user_id,
            first_name=confirmed_user.first_name,  # Извлекаем имя из ConfirmedUser
            last_name=confirmed_user.last_name,  # Извлекаем фамилию из ConfirmedUser
            middle_name=confirmed_user.middle_name,  # Извлекаем отчество из ConfirmedUser
            key=str(uuid.uuid4()),  # Сгенерируем уникальный код
            key_expiry=datetime.utcnow() + CODE_LIFETIME,  # Время жизни кода
        )
        session.add(new_pending_user)
        session.commit()

        # Здесь отправляем код на email пользователя
        # send_confirmation_code(email, new_pending_user.key)

        return {"message": f"Для входа отправлен код на почту {email}."}
    else:
        # Если user_id не найден, отправляем предупреждение на почту о новом user_id
        return send_warning_for_new_user(user_id, email, session)


@router.post("/login/")
def login(user_id: int, email: str, session: Session = Depends(get_session)):
    # Ищем пользователя в базе данных с таким email
    pending_user = session.exec(select(PendingUser).where(PendingUser.email == email)).first()

    if not pending_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    # Проверяем, прошло ли достаточно времени с последней отправки кода
    now = datetime.utcnow()
    if now < pending_user.key_expiry:
        remaining_time = (pending_user.key_expiry - now).total_seconds()
        return {"message": f"Новый код можно будет отправить через {int(remaining_time)} секунд."}

    # Если прошло больше 1 минуты, генерируем новый код
    pending_user.key = str(uuid.uuid4())
    pending_user.key_expiry = now + timedelta(minutes=1)  # Устанавливаем новый срок действия кода на 1 минуту
    session.add(pending_user)
    session.commit()

    # Здесь отправьте новый код на email пользователя
    # send_confirmation_code(email, pending_user.key)

    return {"message": f"Отправлен новый код на почту {email}."}


@router.post("/validate_login/")
def validate_login(email: str, user_id: int, key: str, session: Session = Depends(get_session)):
    # Ищем пользователя в таблице PendingUser по почте
    pending_user = session.exec(select(PendingUser).where(PendingUser.email == email)).first()

    if not pending_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден в ожидании.")

    # Проверяем, истек ли срок действия кода
    if pending_user.key != key or datetime.utcnow() > pending_user.key_expiry:
        raise HTTPException(status_code=400, detail="Неверный или истекший код.")

    # Проверяем, есть ли такой email в таблице ConfirmedUser
    confirmed_user = session.exec(select(ConfirmedUser).where(ConfirmedUser.email == email)).first()

    if not confirmed_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден в подтвержденных.")

    # Проверяем, существует ли user_id в списке confirmed_user.users_ids
    users_ids = json.loads(confirmed_user.users_ids)  # Преобразуем строку JSON обратно в список
    if user_id not in users_ids:
        # Отправляем уведомление о новом user_id
        # send_confirmation_request_to_user(email, user_id)

        return {
            "message": f"Новый user_id {user_id} не найден в списке пользователей. Отправлено уведомление для подтверждения."
        }

    # Если все верно, добавляем user_id в список
    users_ids.append(user_id)
    confirmed_user.users_ids = json.dumps(users_ids)  # Преобразуем обратно в строку JSON
    session.add(confirmed_user)
    session.commit()

    # Удаляем пользователя из PendingUser, так как вход завершен
    session.delete(pending_user)
    session.commit()

    return {"message": "Вход успешен. Новый user_id добавлен в ваш аккаунт."}


# Функция для отправки предупреждения о новом user_id
def send_warning_for_new_user(user_id: int, email: str, session: Session):
    # Здесь отправляем уведомление на почту о том, что новый user_id был замечен
    # send_new_user_warning(email, user_id)

    return {
        "message": f"Новый user_id {user_id} замечен для вашего аккаунта. Мы отправим вам код подтверждения, если это вы."}
