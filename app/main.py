from fastapi import FastAPI

from routers import auth, profiles, ring

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(profiles.router, prefix="/profiles")
app.include_router(ring.router, prefix="/ring")