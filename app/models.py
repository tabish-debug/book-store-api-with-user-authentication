from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, String, Boolean, Float, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    photo = Column(String, nullable=True) # image url which get after upload image
    verified = Column(Boolean, nullable=False, default=False)
    role = Column(String, server_default='user', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    books = relationship("Book", back_populates="user")

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cover_image = Column(String, nullable=True) # image url which get after upload image
    price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User, back_populates="books")
