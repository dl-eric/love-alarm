from bson.objectid import ObjectId
from fastapi import APIRouter, Header, HTTPException, Depends
from starlette.websockets import WebSocket
import asyncio

from api.auth_utils import get_current_active_user
from db.base import db, r
from models import ForeignProfile, User, UserWithId


router = APIRouter()

@router.get('/me', response_model=User)
async def me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.patch('/me')
async def update_me(current_user: User = Depends(get_current_active_user)):
    return "Patch me!"

@router.websocket('/me/ws')
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        # User should send us their location and id
        position = await websocket.receive_text()

        # Message format: "longitude:latitude:userid"
        # TODO Validate message

        data = position.split(':')
        r.geoadd('locations', float(data[0]), float(data[1]), data[2])

        answer = r.georadiusbymember('locations', data[2], 1, unit='km')
        result = list(map(lambda x : x.decode(), answer))
        result = ','.join(result)
        await websocket.send_text(result)

@router.get('/{profile_id}', response_model=ForeignProfile)
async def get_profile(profile_id: str, current_user: User = Depends(get_current_active_user)):
    # TODO: Also send distance information
    try:
        obj_profile_id = ObjectId(profile_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    profile = db.User.find_one({'_id': obj_profile_id}, {'_id': 0, 'first_name': 1, 'last_name': 1, 'profile_pic': 1})

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile