from bson.objectid import ObjectId
from fastapi import APIRouter, Header, HTTPException, Depends
from starlette.websockets import WebSocket
import asyncio
import boto3
import uuid

from app.api.auth_utils import get_current_active_user, get_current_user, get_user_from_token
from app.api.aws_utils import get_image_key
from app.db.base import db, r, aws
from app.models import ForeignProfile, User, UserWithId, PatchUserIn, PatchLocationIn
from app.config import S3_BUCKET_NAME, S3_URL_EXPIRE_TIME, MAX_NUMBER_USER_IMAGES


router = APIRouter()

@router.get('/me', response_model=UserWithId)
async def me(current_user: UserWithId = Depends(get_current_active_user)):
    return current_user

@router.patch('/me')
async def update_me(info: PatchUserIn, current_user: UserWithId = Depends(get_current_active_user)):
    info_without_nulls = {}
    info_dict = info.dict()

    for key in info_dict:
        if info_dict[key] != None:
            info_without_nulls[key] = info_dict[key]

    db.User.update({'phone_number': current_user.phone_number}, {'$set': info_without_nulls})
    return 0

@router.patch('/me/location')
async def update_location(location: PatchLocationIn, current_user: UserWithId = Depends(get_current_active_user)):
    # TODO: Verify location input
    r.geoadd('locations', float(location.longitude), float(location.latitude), current_user.id)
    return 0

@router.post('/me/image')
async def get_presigned_url(current_user: UserWithId = Depends(get_current_active_user)):
    """
    Creates an AWS presigned URL for clients that want to upload images
    """
    image_name = uuid.uuid4()

    if not current_user.images:
        current_user.images = [image_name]
    elif len(current_user.images) >= MAX_NUMBER_USER_IMAGES:
        raise HTTPException(status_code=400, detail="Max images reached")
    else:
        current_user.images.append(image_name)

    try:
        db.User.update({'phone_number': current_user.phone_number}, {'$set': current_user.images})
    except:
        raise HTTPException(status_code=500, detail="Mongo Failed")

    key = get_image_key(UserWithId.id, str(image_name))
    try:
        response = aws.generate_presigned_post(S3_BUCKET_NAME, key, ExpiresIn=S3_URL_EXPIRE_TIME)
    except:
        # Remove from Mongo
        current_user.images.remove(image_name)

        # If Mongo fails here, then we will have a database corruption. Should be fine because clients should realize
        # the image doesn't exist and will call delete_image endpoint.
        db.User.update({'phone_number': current_user.phone_number}, {'$set': current_user.images})

        raise HTTPException(status_code=500, detail="AWS Failed")

    return response

@router.patch('/me/image')
async def reorder_images(current_user: UserWithId = Depends(get_current_active_user), images : list):
    """
    Patches user's images with the given new order. Image list consists of filenames, and the length of the
    given image list must be the same as the number of the user's images, and must contain the same elements.

    User must have more than two images for a successful response
    """
    if not current_user.images or len(current_user.images) < 2:
        raise HTTPException(status_code=400, detail="User has less than 2 images")

    if len(images) != len(current_user.images) and set(images) != set(current_user.images):
        raise HTTPException(status_code=400, detail="Invalid given image list")

    try:
        db.User.update({'phone_number': current_user.phone_number}, {'$set': {'images': images}})
    except:
        raise HTTPException(status_code=500, detail="Mongo Failed to Update")

    return 0

@router.delete('/me/image')
async def delete_image(current_user: UserWithId = Depends(get_current_active_user), image_uuid : str):
    """
    Deletes a given image from S3 for a given user
    """
    if not current_user.images or len(current_user.images) == 0:
        raise HTTPException(status_code=400, detail="User has no images")
        
    key = get_image_key(UserWithId.id, image_uuid)

    # Attempt to delete from S3 first to ensure S3 is always the most up to date
    aws.delete_object(bucket_name=S3_BUCKET_NAME, Key=key)

    # Attempt to delete from Mongo second
    current_user.images.remove(image_uuid)

    try:
        db.User.update({'phone_number': current_user.phone_number}, {'$set': {'images': current_user.images}})
    except:
        raise HTTPException(status_code=500, detail="Mongo Failed to Update")
    
    return 0

@router.websocket('/me/ws')
async def ws_endpoint(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close()
        return

    user = await get_user_from_token(token)
    if not user:
        print('Invalid token')
        await websocket.close()
        return

    await websocket.accept()

    while True:
        # User should send us their location
        position = await websocket.receive_text()

        # Message format: "longitude:latitude:distance:distance unit"
        # TODO Validate message

        data = position.split(':')
        r.geoadd('locations', float(data[0]), float(data[1]), user.id)

        answer = r.georadiusbymember('locations', user.id, int(data[2]), unit=data[3])

        num_winks = 0
        for winker in user.winkers:
            if winker in answer:
                num_winks += 1
        
        await websocket.send_text(str(num_winks))

@router.get('/{profile_id}', response_model=ForeignProfile)
async def get_profile(profile_id: str, current_user: User = Depends(get_current_active_user)):
    # TODO: Also send distance information of the profile?
    try:
        obj_profile_id = ObjectId(profile_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    profile = db.User.find_one({'_id': obj_profile_id}, {'_id': 0, 'first_name': 1, 'last_name': 1, 'profile_pic': 1})

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.get('/')
async def get_nearby(radius: int, current_user: UserWithId = Depends(get_current_active_user)):
    """
    Returns a list of user ids that are within <radius> of current user
    """
    answers = r.georadiusbymember('locations', current_user.id, radius, "km")
    answers.remove(current_user.id.encode()) # Remove current user
    return answers
