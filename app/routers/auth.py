from fastapi import APIRouter

router = APIRouter()

@router.put('/')
async def index():
    return {'hi': 1}

@router.post('/')
async def index():
    return {'hi': 1}