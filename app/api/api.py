from fastapi import APIRouter

from .endpoints import auth, profiles, wink

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=['Auth'])
api_router.include_router(profiles.router, prefix="/profiles", tags=['Profiles'])
api_router.include_router(wink.router, prefix="/wink", tags=['Winking'])