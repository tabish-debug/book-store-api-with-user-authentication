from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import get_db
from ..oauth2 import require_user
from ..models import Base
from ..main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db

def override_require_user():
    return 1

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_user] = override_require_user

client = TestClient(app)