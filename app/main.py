from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, file, user, book

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from . import middleware

"""
All routes request or response data with xml and json both of form.
Its depends on your sending content-type header

##### XML (register user example)  #####

<user>
    <email>example@email.com</email>
    ...
</user>

 ##### JSON (register user example) #####

{ "email":"example@email.com", ... }

"""

app.include_router(file.router, tags=['File'], prefix='/api/file')
app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(user.router, tags=['User'], prefix='/api/user')
app.include_router(book.router, tags=['Store'], prefix='/api/store')

@app.get('/')
def root():
    return {'message': 'server is running'}
