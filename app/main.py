from fastapi import FastAPI
from starlette.websockets import WebSocket

from api import api

app = FastAPI()

app.include_router(api.api_router)