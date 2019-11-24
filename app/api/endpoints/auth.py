from fastapi import APIRouter
import json

from db.base import db
from db.models import User

router = APIRouter()

@router.put('/')
async def index():
    return {'hi': 1}

@router.post('/')
async def create_user(user: User):
    print(user.dict())
    inserted_id = db.User.insert_one(user.dict()).inserted_id

    print(inserted_id)

    return {'message': str(inserted_id)}