import base64
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from sqlalchemy.orm import Session
from . import config, database, models

class Settings(BaseModel):
    authjwt_algorithm: str = config.settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [config.settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_public_key: str = base64.b64decode(
        config.settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        config.settings.JWT_PRIVATE_KEY).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return Settings()

class NotVerified(Exception):
    pass

class UserNotFound(Exception):
    pass

def require_user(db: Session = Depends(database.get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        
        # Check user exist
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise UserNotFound('user no longer exist')
        
        # Check email verified
        if not user.verified:
            raise NotVerified('email not verified')

    except Exception as e:
        error = e.__class__.__name__

        # Check token not exist 
        if error == 'MissingTokenError':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you are not logged in')
        
        # Check user not found
        if error == 'UserNotFound':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user no longer exist')
        
        # Check email not verified
        if error == 'NotVerified':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='please verify your account')
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired')
    
    # Return user id
    return user_id
