import uuid
from datetime import datetime

from pydantic import AnyUrl

from config import settings
from send_email import email_sender


async def handle_existing_user(existing_user, url_type: str, param: str, session):
    now = datetime.utcnow()

    # Проверяем, не истек ли срок действия кода
    if now < existing_user.key_expiry:
        remaining_time = (existing_user.key_expiry - now).total_seconds()
        return {"message": f"Новей код для подтверждения будет отправлен через {int(remaining_time)} секунд."}

    # Если прошло больше времени, чем 1 минута, обновляем ключ и срок действия
    existing_user.key = str(uuid.uuid4())
    existing_user.key_expiry = now + settings.min_wait_time

    # Добавляем изменения в сессию и сохраняем их
    session.add(existing_user)
    session.commit()

    # Обновляем объект, чтобы получить актуальные данные
    session.refresh(existing_user)

    # Возвращаем новый ключ
    url = f"{settings.api_site}/{url_type}/validate/?{param}&key={existing_user.key}"

    await email_sender.send_email(
        subject="NextAuth Registration",
        body=f"Перейдите по ссылке, чтобы подтвердить свой профиль.\nСсылка: {url}",
        recipients=[existing_user.email],
    )

    return {"message": f"Отправлен новый код подтверждения на почту!"}
