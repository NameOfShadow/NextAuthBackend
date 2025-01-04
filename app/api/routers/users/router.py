from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.confirmeduser.crud import get_all_confirmed_user_userid
from app.db.database import get_session

router = APIRouter()


@router.get("confirmed/{id}/")
async def list_users(id: int, session: Session = Depends(get_session)):
    return get_all_confirmed_user_userid(session, id)
