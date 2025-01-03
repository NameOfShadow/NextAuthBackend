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

def get_all_confirmed_user_userid(session: Session, user_id: int) -> ConfirmedUser:
    query = select(ConfirmedUser).where(text(f"json_extract(users_ids, '$') LIKE '%{user_id}%'"))
    return session.exec(query).all()

def get_confirmed_user_email(session: Session, email: int) -> ConfirmedUser:
    return session.exec(select(ConfirmedUser).where(ConfirmedUser.email == email)).first()

def get_all_confirmed_users(session: Session):
    return session.exec(select(ConfirmedUser)).all()
