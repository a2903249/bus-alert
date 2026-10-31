from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="未登入或登入已過期")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="使用者不存在")
    return user