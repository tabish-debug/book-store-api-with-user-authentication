from uuid import uuid4
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def generate_filename(name: str):
    _ , ext = name.rsplit('.', 1)
    return (f"{uuid4()}.{ext}", ext)

def write_file(path, contents):
    with open(path, 'wb') as f:
        f.write(contents)

def model_to_dict(model, exclude=[]):
    new_dict = {}
    for column in model.__table__.columns:
        if column.name not in exclude:
            new_dict[column.name] = str(getattr(model, column.name))
    return new_dict

def multiple_model_to_dict(models, exclude=[]):
    array = []
    total = 0
    for model in models:
        array.append(model_to_dict(model[0], exclude=exclude))
        total = model[1]
    return (array, total)