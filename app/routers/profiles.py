from fastapi import APIRouter

router = APIRouter()

@router.get('/me')
async def me():
    return "It's me"

@router.patch('/me')
async def update_me():
    return "Patch me"

@router.get('/{profile_id}')
async def get_profile(profile_id: int):
    return profile_id

@router.get('/')
async def get_nearby():
    return 0