from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    last_name: str
    profile_pic: str
    winkers: list = []

class ForeignProfile(BaseModel):
    first_name: str
    last_name: str
    profile_pic: str

class UserId(BaseModel):
    user_id: str