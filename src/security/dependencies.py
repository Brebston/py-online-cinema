from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from security.http import get_token

from database import get_db
from database.models.accounts import UserModel

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        db: Annotated[str, Depends(get_db)],
        access_token: Annotated[str, Depends(get_token)],
        jwt_manager: Annotated[str, Depends(get_jwt_auth_manager)],
) -> UserModel:
    try: