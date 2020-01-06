from fastapi import FastAPI
from starlette.websockets import WebSocket

from .api import api
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, DEBUG_MODE

if DEBUG_MODE:
    print("***WARNING 1: STARTING IN DEBUG MODE***")
    print("***WARNING 2: STARTING IN DEBUG MODE***")
    print("***WARNING 3: STARTING IN DEBUG MODE***")

# FastAPI
app = FastAPI()
app.include_router(api.api_router)