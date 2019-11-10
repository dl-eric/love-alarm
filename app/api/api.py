from fastapi import APIRouter

from .endpoints import auth, profiles, ring

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(profiles.router, prefix="/profiles")
api_router.include_router(ring.router, prefix="/ring")