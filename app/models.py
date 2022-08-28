from uuid import uuid4
from sqlalchemy import TIMESTAMP, Column, String, Boolean, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    photo = Column(String, nullable=True) # image url which get after upload image
    verified = Column(Boolean, nullable=False, server_default='False')
    role = Column(String, server_default='user', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    books = relationship("Book", back_populates="user")

class Book(Base):
    __tablename__ = "book"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cover_image = Column(String, nullable=True) # image url which get after upload image
    price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(User, back_populates="books")
