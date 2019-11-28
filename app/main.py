from fastapi import FastAPI
from starlette.websockets import WebSocket

from .api import api
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# FastAPI
app = FastAPI()
app.include_router(api.api_router)