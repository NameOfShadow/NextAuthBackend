from sqlmodel import Session, select, text

from app.db.confirmeduser import model


def create_confirmed_user(session: Session, user: model.ConfirmedUser) -> model.ConfirmedUser:
    session.add(user)
    session.commit()
    session.refresh(user)  # Обновить объект для получения ID
    return user


def get_confirmed_user(session: Session, user_id: int) -> model.ConfirmedUser:
    query = select(model.ConfirmedUser).where(text(f"json_extract(users_ids, '$') LIKE '%{user_id}%'"))
    return session.exec(query).first()


def get_all_confirmed_users(session: Session):
    return session.exec(select(model.ConfirmedUser)).all()
