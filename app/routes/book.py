from typing import Optional
import math

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import Session

from .. import models, database, schema, oauth2, utils
from ..custom import CustomRequest, CustomResponse, CustomRoute

router = APIRouter()
router.route_class = CustomRoute

"""
##### All Book Routes #####

: Get all books and search book
: Create a book
: Get all books by user
: Get single book
: Update existing book
: Delete any book

Media type: 
You also set Accept headers for different response
like request in json and response in xml and vice versa

media_type = request.headers.get('Accept')

"""

@router.get('/books')
def books(request: CustomRequest, response: CustomResponse, page: int, 
    per_page: int, search: Optional[str] = '', db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')


    # Get search or/and pagination query
    p = page - 1
    books = db.query(models.Book, func.count(models.Book.id).over().label("total")).group_by(
        models.Book.id).filter(or_(models.Book.title.contains(search), 
        models.Book.description.contains(search))).limit(per_page).offset(p * per_page)
    

    # Model to dict and exclude extra field
    rows, total = utils.multiple_model_to_dict(models=books, exclude=['user_id'])

    # Add pagination summary
    
    summary = dict(
        page=page, 
        per_page=per_page, 
        total=total, 
        total_pages= math.ceil(total / per_page)
    )
    data = dict(rows=rows, summary=summary)

    # Set response and status code 
    response = CustomResponse(content=data, media_type=media_type, custom_root='books')
    response.status_code = status.HTTP_200_OK

    # Return response
    return response

@router.post('/books')
def create_book(request: CustomRequest, response: CustomResponse, payload: schema.CreateBookSchema, 
    user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')
    
    # Add user id in book payload
    payload.user_id = user_id
    
    # Create new book
    new_book = models.Book(**payload.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # Model to dict and Exclude extra field
    data = utils.model_to_dict(model=new_book, exclude=['user_id'])
    
    # Set response new book and status code
    response = CustomResponse(content=data, media_type=media_type, custom_root='book')
    response.status_code = status.HTTP_201_CREATED
     
    # Return response 
    return response

@router.get('/books/user')
def books_by_user(request: CustomRequest, response: CustomResponse, page: int, per_page: int, 
    user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Get book query
    p = page - 1
    books = db.query(models.Book, func.count(models.Book.id).over().label("total")).group_by(
        models.Book.id).filter(models.Book.user_id == user_id).limit(per_page).offset(p * per_page)

    # Model to dict and exclude extra field
    rows, total = utils.multiple_model_to_dict(models=books, exclude=['user_id'])

    # Add pagination summary
    summary = dict(
        page=page, 
        per_page=per_page, 
        total=total, 
        total_pages= math.ceil(total / per_page)
    )
    data = dict(rows=rows, summary=summary)

    # Set response and status code 
    response = CustomResponse(content=data, media_type=media_type, custom_root='books')
    response.status_code = status.HTTP_200_OK

    # Return response
    return response

@router.get('/book/{id}')
def book(request: CustomRequest, response: CustomResponse, id: str,
    user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Get book query
    book = db.query(models.Book).filter(and_(models.Book.id == id,
        models.Book.user_id == user_id)).first()
    
    # Check book not found
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")
    
    # Model to dict and exclude extra fields
    data = utils.model_to_dict(model=book, exclude=["user_id"])

    # Set response and status code
    response = CustomResponse(content=data, media_type=media_type, custom_root='book')
    response.status_code = status.HTTP_200_OK
    
    # Send response
    return response

@router.put('/book/{id}')
def create_book(request: CustomRequest, response: CustomResponse, payload: schema.UpdateBookSchema, 
    id: str, user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')
    
    # Get book query
    book = db.query(models.Book).filter(and_(models.Book.id == id,
        models.Book.user_id == user_id))
     
    # Check if book not found 
    if not book.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")
    
    # Update book
    book.update(payload.dict())
    db.commit()
    
    # Set response and status code  
    response = CustomResponse(content={ "detail" : "book updated successfully" }, 
        media_type=media_type, custom_root='book')
    response.status_code = status.HTTP_205_RESET_CONTENT
    
    # Send response
    return response

@router.delete('/book/{id}')
def delete_book(request: CustomRequest, response: CustomResponse, 
    id: str, user_id: str = Depends(oauth2.require_user), db: Session = Depends(database.get_db)):
    # Get content type header
    media_type = request.headers.get('Content-Type')

    # Get book query
    book = db.query(models.Book).filter(and_(models.Book.id == id,
        models.Book.user_id == user_id))

    # Check if book not found 
    if not book.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")
    
    # Delete book
    book.delete()
    db.commit()
    
    # Set response and status code
    response = CustomResponse(content={ "detail" : "book deleted successfully" }, 
        media_type=media_type, custom_root='book')
    response.status_code = status.HTTP_204_NO_CONTENT

    return response
