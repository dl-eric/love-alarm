from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
import nexmo

from app.db.base import db
from app.models import User, PhoneNumber, RequestId, ValidateIn, Token
from app.api.auth_utils import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, NEXMO_API_KEY, NEXMO_SECRET


# Nexmo
nex_client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_SECRET)

router = APIRouter()

@router.post('/stop_login')
async def stop_login(code: RequestId):
    """
    Stops the Nexmo phone number validation flow for a given request id
    """

    response = nex_client.cancel_verification(code.request_id)
    
    if response['status'] == '6':
        # Nexmo says it's invalid
        db.User.update({'request_id': code.request_id}, {'$set': {'request_id': None}})
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=response['error_text']
        )
    elif response['status'] != '0':
        # Something went wrong
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response['error_text']
        )

    # Success!
    db.User.update({'request_id': code.request_id}, {'$set': {'request_id': None}})
    return {'message': 'success'}

@router.post('/start_login', response_model=RequestId)
async def start_login(phone_num : PhoneNumber):
    """
    Starts the Nexmo verify flow for a given phone number. If the phone number is new,
    we create a new user for it. Otherwise, we simply use the existing user.
    """

    # Request to verify this phone number
    response = nex_client.start_verification(number=phone_num.phone_number, brand="Wink")
    
    # Get back request_id
    if response["status"] == "0":
        print("Started verification request_id is %s" % (response["request_id"]))

        # TODO: Check for error 
        try:
            db.User.update_one(
                {'phone_number': phone_num.phone_number}, 
                { '$set': {'request_id': response['request_id']}}, 
                upsert=True
            )
            return {'request_id': response['request_id']}
        except:
            # Redis error. Cancel the verification.
            response = nex_client.cancel_verification(response['request_id'])
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
    elif response['status'] == '3':
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=response['error_text']
        )
    else:
        print("Error: %s" % response["error_text"])
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["error_text"]
        )

@router.post('/validate_code', response_model=Token)
async def validate_code(code: ValidateIn):
    """
    Returns an access token if the code is verified against the request id
    """

    # Validate if the code is valid for request_id
    user = db.User.find_one({'request_id': code.request_id})
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Request Id not found"
        )

    response = nex_client.check_verification(code.request_id, code=code.code)
    if response["status"] == "0":
        print("Verification successful, event_id is %s" % (response["event_id"]))
          # Is valid
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['phone_number']}, expires_delta=access_token_expires
        )
        db.User.update({'request_id': code.request_id}, {'$set': {'request_id': None}})
        return {"access_token": access_token, "token_type": "bearer"}
    elif response['status'] == '6':
        # Nexmo says it's invalid
        db.User.update({'request_id': code.request_id}, {'$set': {'request_id': None}})
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=response['error_text']
        )
    else:
        print("Error: %s" % response["error_text"])
        # Is not valid
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect code"
        )