from datetime import timedelta
from fastapi import APIRouter, Response, status, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import schema, models, utils, database, config, oauth2
from ..oauth2 import AuthJWT
from ..custom import CustomRequest, CustomResponse, CustomRoute

router = APIRouter()
router.route_class = CustomRoute

ACCESS_TOKEN_EXPIRES_IN = config.settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = config.settings.REFRESH_TOKEN_EXPIRES_IN

"""
##### All Auth Routes #####

: Register new user
: Login user (set cookies with refresh, access and login and response access token)
: Refresh access token (create new access token also update in cookies)
: Logout user (unset cookies)

Media type: 
You also set Accept headers for different response
like request in json and response in xml and vice versa

media_type = request.headers.get('Accept')

"""

@router.post('/register')
async def create_user(request: CustomRequest, response: CustomResponse, payload: schema.CreateUserSchema,
    db: Session = Depends(database.get_db)):
    
    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Check if user already exist
    user = db.query(models.User).filter(or_(models.User.email == EmailStr(payload.email.lower()), 
        models.User.username == payload.username)).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exist')
     
    # Compare passwords 
    if payload.password != payload.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    
    # Hash the password
    payload.password = utils.hash_password(payload.password)

    # Set payload  
    del payload.password_confirm
    payload.role = 'user'
    payload.verified = True
    payload.email = EmailStr(payload.email.lower())
    
    # Create new user
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Model to dict and Exclude extra field
    data = utils.model_to_dict(model=new_user,
        exclude=['password', 'role', 'verified'])

    # Set response new user and status code
    response = CustomResponse(content=data, media_type=media_type, custom_root='user')
    response.status_code = status.HTTP_201_CREATED

    # Send response
    return response

@router.post('/login')
def login(
    request: CustomRequest, response: CustomResponse, payload: schema.LoginUserSchema,  
        db: Session = Depends(database.get_db), Authorize: AuthJWT = Depends()):

    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Check user is exist
    user = db.query(models.User).filter(
        models.User.email == EmailStr(payload.email.lower())).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='incorrect email and password')
    
    # Check user email is verified
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="please verify your email address")

    # Check password is valid
    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='incorrect email and password')
    
    # Create access and refresh tokens
    access_token = Authorize.create_access_token(subject=str(user.id), 
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Authorize.create_refresh_token(subject=str(user.id), 
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))
    
    # Set response with success and access token and status code
    response = CustomResponse({'status': 'success', 'access_token': access_token}, 
        media_type=media_type, custom_root='user')
    response.status_code = status.HTTP_200_OK

    # Store access and refresh token in cookies
    response.set_cookie(
        key='access_token', value=access_token, max_age=ACCESS_TOKEN_EXPIRES_IN * 60, 
        expires= ACCESS_TOKEN_EXPIRES_IN * 60, path='/', domain=None, secure=False, httponly=False, samesite="lax"
    )
    response.set_cookie(
        key='refresh_token', value=refresh_token, max_age=REFRESH_TOKEN_EXPIRES_IN * 60, 
        expires= REFRESH_TOKEN_EXPIRES_IN * 60, path='/', domain=None, secure=False, httponly=False, samesite="lax"
    )
    response.set_cookie(
        key='logged_in', value=True, max_age=REFRESH_TOKEN_EXPIRES_IN * 60, 
        expires= REFRESH_TOKEN_EXPIRES_IN * 60, path='/', domain=None, secure=False, httponly=False, samesite="lax"
    )
     
    # Send response 
    return response

@router.get('/refresh')
def refresh_token(request: CustomRequest, response: CustomResponse, Authorize: AuthJWT = Depends(), 
    db: Session = Depends(database.get_db)):
    
    # Get content type header
    media_type = request.headers.get('Content-Type')

    try:
        # Check required refresh token 
        Authorize.jwt_refresh_token_required()

        # Get user id from token
        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not refresh access token')

        # Check user is exist
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user belongs to this token not exist')
        
        # Create new access token
        access_token = Authorize.create_access_token(subject=str(user.id),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    except Exception as e:
        error = e.__class__.__name__
        # Check if refresh token no exist error
        if error == 'MissingTokenError':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='please provide refresh token')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)

    # Set response with success and access token and status code
    response = CustomResponse({ "status": "success", "access_token": access_token }, 
        media_type=media_type, custom_root='user')
    response.status_code = status.HTTP_200_OK
    
    # Set new access token and logged in cookies 
    response.set_cookie(
        key='access_token', value=access_token, max_age=ACCESS_TOKEN_EXPIRES_IN * 60, 
        expires= ACCESS_TOKEN_EXPIRES_IN * 60, path='/', domain=None, secure=False, httponly=False, samesite="lax"
    )
    response.set_cookie(
        key='logged_in', value=True, max_age=REFRESH_TOKEN_EXPIRES_IN * 60, 
        expires= REFRESH_TOKEN_EXPIRES_IN * 60, path='/', domain=None, secure=False, httponly=False, samesite="lax"
    )
    
    # Send response
    return response

@router.get('/logout')
def logout(request: CustomRequest, response: Response, Authorize: AuthJWT = Depends(), 
    user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    
    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Get user
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Set success and logout user email and status code
    response = CustomResponse({ "status": "success", "email": user.email }, 
        media_type=media_type, custom_root='user')
    response.status_code = status.HTTP_200_OK

    # Unset all cookies
    response.set_cookie('logged_in', '', -1)
    Authorize.unset_jwt_cookies(response)
    
    # Send response
    return response
