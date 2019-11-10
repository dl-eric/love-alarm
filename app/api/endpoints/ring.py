from fastapi import APIRouter

router = APIRouter()

@router.post('/{profile_id}')
async def ring_profile(profile_id: int):
    return profile_id

@router.get('/')
async def get_rings():
    return 0