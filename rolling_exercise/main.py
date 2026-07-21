from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from typing import List,  Annotated
import datetime
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import logging

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PollutantsBase(BaseModel):
    id: int
    date: datetime
    city: str
    pm25: float
    no2: float

class AlertsBase(BaseModel):

def get_db():
    db = SessionLocal()
    try:
        yield
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    for line in file:
        vals = line.strip().split(",")
        if len(vals) != 5: # log bad row
            print("Missing column values")
            continue
        
