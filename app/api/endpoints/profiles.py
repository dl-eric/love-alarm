from bson.objectid import ObjectId
from fastapi import APIRouter, Header, HTTPException, Depends
from starlette.websockets import WebSocket
import asyncio
import boto3
import uuid

from app.api.auth_utils import get_current_active_user, get_current_user, get_user_from_token
from app.db.base import db, r, aws
from app.models import ForeignProfile, User, UserWithId, PatchUserIn, PatchLocationIn
from app.config import S3_BUCKET_NAME, S3_URL_EXPIRE_TIME


router = APIRouter()

@router.get('/me', response_model=UserWithId)
async def me(current_user: UserWithId = Depends(get_current_active_user)):
    return current_user

@router.patch('/me')
async def update_me(info: PatchUserIn, current_user: UserWithId = Depends(get_current_active_user)):
    info_without_nulls = {}
    info_dict = info.dict()

    for key in info_dict:
        if info_dict[key] != None:
            info_without_nulls[key] = info_dict[key]

    db.User.update({'phone_number': current_user.phone_number}, {'$set': info_without_nulls})
    return 0

@router.patch('/me/location')
async def update_location(location: PatchLocationIn, current_user: UserWithId = Depends(get_current_active_user)):
    # TODO: Verify location input
    r.geoadd('locations', float(location.longitude), float(location.latitude), current_user.id)
    return 0

@router.get('/me/image')
async def get_presigned_url(current_user: UserWithId = Depends(get_current_active_user)):
    image_name = uuid.uuid4()
    key = UserWithId.id + '/images/' + str(image_name)
    try:
        response = aws.generate_presigned_post(S3_BUCKET_NAME, key, ExpiresIn=S3_URL_EXPIRE_TIME)
    except:
        raise HTTPException(status_code=500, detail="AWS Failed")

    return response

@router.websocket('/me/ws')
async def ws_endpoint(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close()
        return

    user = await get_user_from_token(token)
    if not user:
        print('Invalid token')
        await websocket.close()
        return

    await websocket.accept()

    while True:
        # User should send us their location
        position = await websocket.receive_text()

        # Message format: "longitude:latitude:distance:distance unit"
        # TODO Validate message

        data = position.split(':')
        r.geoadd('locations', float(data[0]), float(data[1]), user.id)

        answer = r.georadiusbymember('locations', user.id, int(data[2]), unit=data[3])

        num_winks = 0
        for winker in user.winkers:
            if winker in answer:
                num_winks += 1
        
        await websocket.send_text(str(num_winks))

@router.get('/{profile_id}', response_model=ForeignProfile)
async def get_profile(profile_id: str, current_user: User = Depends(get_current_active_user)):
    # TODO: Also send distance information of the profile?
    try:
        obj_profile_id = ObjectId(profile_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    profile = db.User.find_one({'_id': obj_profile_id}, {'_id': 0, 'first_name': 1, 'last_name': 1, 'profile_pic': 1})

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.get('/')
async def get_nearby(radius: int, current_user: UserWithId = Depends(get_current_active_user)):
    """
    Returns a list of user ids that are within <radius> of current user
    """
    answers = r.georadiusbymember('locations', current_user.id, radius, "km")
    answers.remove(current_user.id.encode()) # Remove current user
    return answers
