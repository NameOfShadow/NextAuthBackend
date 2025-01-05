from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.confirmeduser.crud import get_all_confirmed_user_userid
from app.db.database import get_session

router = APIRouter()


@router.get("/confirmed/{user_id}/")
async def list_users(user_id: int, session: Session = Depends(get_session)):
    return get_all_confirmed_user_userid(session, user_id)
