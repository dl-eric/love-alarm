from bson.objectid import ObjectId
from fastapi import APIRouter, Header, HTTPException, Depends
from starlette.websockets import WebSocket
import asyncio

from api.auth_utils import get_current_active_user, get_current_user
from db.base import db, r
from models import ForeignProfile, User, UserWithId


router = APIRouter()

@router.get('/me', response_model=UserWithId)
async def me(current_user: UserWithId = Depends(get_current_active_user)):
    return current_user

@router.patch('/me')
async def update_me(current_user: UserWithId = Depends(get_current_active_user)):
    return "Patch me!"

@router.websocket('/me/ws')
async def ws_endpoint(websocket: WebSocket, token: str = None, distance: int = None):
    if not token or not distance:
        await websocket.close()
        return

    try:
        user = await get_current_user(token)
    except:
        await websocket.close()
        return

    await websocket.accept()

    while True:
        # User should send us their location
        position = await websocket.receive_text()

        # Message format: "longitude:latitude"
        # TODO Validate message

        data = position.split(':')
        r.geoadd('locations', float(data[0]), float(data[1]), user.id)

        answer = r.georadiusbymember('locations', user.id, distance, unit='km')

        num_winks = 0
        for winker in current_user.winkers:
            if winker in answer:
                num_winks += 1

        await websocket.send_text(num_winks)

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
    return r.georadiusbymember('locations', current_user.id, radius, "km")