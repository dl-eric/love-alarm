from bson.objectid import ObjectId
from fastapi import APIRouter, Header
from starlette.websockets import WebSocket
import asyncio

from db.base import db, r
from db.models import ForeignProfile

router = APIRouter()

@router.get('/me')
async def me():
    return "It's me"

@router.patch('/me')
async def update_me():
    return "Patch me"

@router.websocket('/me/ws')
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    a = 0
    while True:
        a += 1
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
async def get_profile(profile_id: str):
    profile = db.User.find_one({'_id': ObjectId(profile_id)}, {'_id': 0})
    return profile

@router.get('/')
async def get_nearby(token: int = Header(None)):
    print(token)
    return 0