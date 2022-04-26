from typing import Optional, List

import uvicorn

# from fastapi import UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI  #, Depends, Request
# from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer


SQLALCHEMY_DATABASE_URL = f'sqlite:///sqlite.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# from PIL import Image
# import pytesseract
# print(pytesseract.image_to_string(Image.open('test.png')))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


from app import models
from app import views

Base.metadata.create_all(bind=engine)
