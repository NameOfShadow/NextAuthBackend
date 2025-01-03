from sqlmodel import Session, select

from app.db.loginuser.model import LoginUser


def create_login_user(session: Session, user: LoginUser) -> LoginUser:
    session.add(user)
    session.commit()
    session.refresh(user)  # Обновить объект для получения ID
    return user


def get_login_user(session: Session, email: str) -> LoginUser:
    return session.exec(select(LoginUser).where(LoginUser.email == email)).first()


def get_all_login_users(session: Session):
    return session.exec(select(LoginUser)).all()


def delete_expired_login_users(session: Session):
    from datetime import datetime
    expired_users = session.exec(select(LoginUser).where(LoginUser.key_expiry < datetime.utcnow())).all()
    for user in expired_users:
        session.delete(user)
    session.commit()
