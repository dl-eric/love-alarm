from pydantic import BaseModel

class User(BaseModel):
    phone_number: str
    first_name: str
    last_name: str = None
    profile_pic: str = None
    winkers: list = []

class UserInDB(User):
    password: str

class UserWithId(UserInDB):
    id: str

class ForeignProfile(BaseModel):
    first_name: str
    last_name: str
    profile_pic: str

class UserId(BaseModel):
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: str = None