# from pydantic import BaseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Float, String, Integer, ForeignKey
from app import Base


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    books = relationship("Book", backref="author")


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    author_id = Column(Integer, ForeignKey("author.id"))
