from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.db.base import db
from app.models import UserId, User, UserWithId
from app.api.auth_utils import get_current_active_user

router = APIRouter()

@router.post('/{profile_id}')
async def wink_profile(profile_id: str, current_user: UserWithId = Depends(get_current_active_user)):
    try:
        user_id = ObjectId(profile_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    if profile_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't wink at yourself")

    profile = db.User.find_one({'_id': user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    winkers = profile['winkers']
    
    if current_user.id in winkers:
        raise HTTPException(status_code=400, detail="Already winked this user")

    winkers.append(current_user.id)
    db.User.update({'_id': user_id}, { '$set': {'winkers': winkers}})

    return {"message": "Successfully winked"}

@router.delete('/{profile_id}')
async def unwink_profile(profile_id: str, current_user: UserWithId = Depends(get_current_active_user)):
    try:
        user_id = ObjectId(profile_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    if profile_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't unwink at yourself")

    profile = db.User.find_one({'_id': user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    winkers = profile['winkers']

    try:
        winkers.remove(current_user.id)
    except:
        raise HTTPException(status_code=400, detail="Already unwinked/not winked")

    db.User.update({'_id': user_id}, { '$set': {'winkers': winkers}})

    return {"message": "Successfully unwinked"}