import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from database import get_db
from logger import logger
from services import alerts

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)

@router.get("", response_model=list[schemas.AlertsBase])
def get_all_alerts(db: Session = Depends(get_db)):
    logger.info("Retrieving all alerts")
    return alerts.get_all(db)

@router.get("/date", response_model=list[schemas.AlertsBase])
def get_alerts_by_date(
    date: datetime.date,
    db: Session = Depends(get_db),
):
    logger.info(f"Retrieving alerts for date: {date}")
    return alerts.get_by_date(db, date)

@router.get("/city", response_model=list[schemas.AlertsBase])
def get_alerts_by_city(
    city: str,
    db: Session = Depends(get_db),
):
    logger.info(f"Retrieving alerts for city: {city}")
    return alerts.get_by_city(db, city)