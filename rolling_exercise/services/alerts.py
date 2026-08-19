import datetime

from sqlalchemy.orm import Session

import models

def get_all(db: Session):
    return db.query(models.Alerts).all()

def get_by_date(db: Session, date: datetime.date):
    return (
        db.query(models.Alerts)
        .filter(models.Alerts.date == date)
        .all()
    )

def get_by_city(db: Session, city: str):
    return (
        db.query(models.Alerts)
        .filter(models.Alerts.city.ilike(city.strip()))
        .all()
    )