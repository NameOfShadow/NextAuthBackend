from sqlmodel import Session, select

from app.db.pendinguser.model import PendingUser


def create_pending_user(session: Session, user: PendingUser) -> PendingUser:
    session.add(user)
    session.commit()
    session.refresh(user)  # Обновить объект для получения ID
    return user


def get_pending_user(session: Session, email: str) -> PendingUser:
    return session.exec(select(PendingUser).where(PendingUser.email == email)).first()


def get_all_pending_users(session: Session):
    return session.exec(select(PendingUser)).all()


def delete_expired_pending_users(session: Session):
    from datetime import datetime
    expired_users = session.exec(
        select(PendingUser).where(PendingUser.key_expiry < datetime.utcnow())).all()
    for user in expired_users:
        session.delete(user)
    session.commit()
