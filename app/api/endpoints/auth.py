from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db.base import db
from models import User, UserInDB
from api.auth_utils import get_password_hash, authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/signup', status_code=201)
async def create_user(user: UserInDB):
    # Check if user already exists
    existing = db.User.find({'phone_number': user.phone_number})
    if existing:
        raise HTTPException(409, detail="User already exists")

    user_dict = user.dict()
    user_dict['password'] = get_password_hash(user_dict['password'])
    db.User.insert_one(user_dict)

    return {'message': 'Successfully created user!'}