from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import models, oauth2, database, utils
from ..custom import CustomRequest, CustomResponse, CustomRoute

router = APIRouter()
router.route_class = CustomRoute

"""
Route return current login user

Media type: 
You also set Accept headers for different response
like request in json and response in xml and vice versa

media_type = request.headers.get('Accept')

"""

@router.get('/me',)
def get_current_user(request: CustomRequest, response: CustomResponse, 
    db: Session = Depends(database.get_db), user_id: str = Depends(oauth2.require_user)):
    # Get content type header
    media_type = request.headers.get('Content-Type')
    
    # Get current user
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Model to dict and Exclude extra field
    data = utils.model_to_dict(model=user, exclude=['password', 'role', 'verified'])

    # Set user with response and status code  
    response = CustomResponse(content=data, media_type=media_type, custom_root='user')
    response.status_code = status.HTTP_200_OK

    return response
