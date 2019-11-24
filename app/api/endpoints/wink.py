from bson.objectid import ObjectId
from fastapi import APIRouter

from db.base import db
from db.models import UserId

router = APIRouter()

@router.post('/{profile_id}')
async def wink_profile(profile_id: str, curr_user: UserId):
    user_id = ObjectId(profile_id)

    winkers = db.User.find_one({'_id': user_id})['winkers']
    winkers.append(curr_user.user_id)
    db.User.update({'_id': user_id}, { '$set': {'winkers': winkers}})

    return profile_id

@router.post('/{profile_id}')
async def unwink_profile(profile_id: str, curr_user: UserId):
    return profile_id

@router.get('/')
async def get_winks():
    return 0