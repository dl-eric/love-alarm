from pydantic import BaseModel

class User(BaseModel):
    phone_number: str
    first_name: str = None
    last_name: str = None
    profile_pic: str = None
    images: list = []
    winkers: list = []

class UserWithId(User):
    id: str

class ForeignProfile(BaseModel):
    first_name: str
    last_name: str
    profile_pic: str = None

class UserId(BaseModel):
    user_id: str

class PatchUserIn(BaseModel):
    first_name: str = None
    last_name: str = None
    profile_pic: str = None

class PatchLocationIn(BaseModel):
    longitude: str
    latitude: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: str = None

class PhoneNumber(BaseModel):
    phone_number: str

class RequestId(BaseModel):
    request_id: str

class ValidateIn(BaseModel):
    request_id: str
    code: str