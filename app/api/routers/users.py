from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from app.db.confirmeduser.crud import get_confirmed_user
from app.db.database import get_session

router = APIRouter()


@router.get("confirmed/{id}/")
def list_users(id: int, session: Session = Depends(get_session)):
    return get_confirmed_user(session, id)
