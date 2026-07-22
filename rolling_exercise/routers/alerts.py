import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, get_db
from logger import logger

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=list[schemas.AlertsBase])
def get_all_alerts(db: Session = Depends(get_db)):
    logger.info("Retrieving all alerts")
    return db.query(models.Alerts).all()


@router.get("/date", response_model=list[schemas.AlertsBase])
def get_alerts_by_date(date: datetime.date, db: Session = Depends(get_db)):
    logger.info(f"Retrieving alerts for date: {date}")
    return db.query(models.Alerts).filter(models.Alerts.date == date).all()


@router.get("/city", response_model=list[schemas.AlertsBase])
def get_alerts_by_city(city: str, db: Session = Depends(get_db)):
    logger.info(f"Retrieving alerts for city: {city}")
    alerts = db.query(models.Alerts).filter(
        models.Alerts.city.ilike(city.strip())
    ).all()
    return alerts