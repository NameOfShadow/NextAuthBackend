from sqlmodel import Session, select

from app.db.loginuser import model


def create_login_user(session: Session, user: model.LoginUser) -> model.LoginUser:
    session.add(user)
    session.commit()
    session.refresh(user)  # Обновить объект для получения ID
    return user


def get_login_user(session: Session, email: str) -> model.LoginUser:
    return session.exec(select(model.LoginUser).where(model.LoginUser.email == email)).first()


def get_all_login_users(session: Session):
    return session.exec(select(model.LoginUser)).all()


def delete_expired_login_users(session: Session):
    from datetime import datetime
    expired_users = session.exec(select(model.LoginUser).where(model.LoginUser.key_expiry < datetime.utcnow())).all()
    for user in expired_users:
        session.delete(user)
    session.commit()
