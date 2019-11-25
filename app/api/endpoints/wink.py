from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException

from db.base import db
from db.models import UserId

router = APIRouter()

@router.post('/{profile_id}')
async def wink_profile(profile_id: str, curr_user: UserId):
    try:
        user_id = ObjectId(profile_id)
        ObjectId(curr_user.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    if profile_id == curr_user.user_id:
        raise HTTPException(status_code=400, detail="Can't wink at yourself")

    profile = db.User.find_one({'_id': user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    winkers = profile['winkers']
    
    if curr_user.user_id in winkers:
        raise HTTPException(status_code=400, detail="Already winked this user")

    winkers.append(curr_user.user_id)
    db.User.update({'_id': user_id}, { '$set': {'winkers': winkers}})

    return {"message": "Successfully winked"}

@router.delete('/{profile_id}')
async def unwink_profile(profile_id: str, curr_user: UserId):
    try:
        user_id = ObjectId(profile_id)
        ObjectId(curr_user.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    if profile_id == curr_user.user_id:
        raise HTTPException(status_code=400, detail="Can't unwink at yourself")

    profile = db.User.find_one({'_id': user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    winkers = profile['winkers']

    try:
        winkers.remove(curr_user.user_id)
    except:
        raise HTTPException(status_code=400, detail="Already unwinked/not winked")

    db.User.update({'_id': user_id}, { '$set': {'winkers': winkers}})

    return {"message": "Successfully unwinked"}