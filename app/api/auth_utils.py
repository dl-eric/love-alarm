from datetime import datetime, timedelta
from bson.objectid import ObjectId

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows
from jwt import PyJWTError
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from app.db.base import db
from app.models import User, UserWithId, TokenData
from app.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2()

def get_user(phone_number: str):
    user = db.User.find_one({'phone_number': phone_number})
    user['id'] = str(user['_id'])
    return UserWithId(**user)


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get('sub')
        if phone_number is None:
            return None
    except PyJWTError:
        return None

    return get_user(phone_number=phone_number)

async def get_current_user(header: str = Depends(oauth2_scheme)):
    heading, token = get_authorization_scheme_param(header)

    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_user_from_token(token)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserWithId = Depends(get_current_user)):
    # If we want to mark certain users active, we would check it here.
    return current_user