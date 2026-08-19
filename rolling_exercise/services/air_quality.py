import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

import models

def get_by_date(
    db: Session,
    start_date: datetime.date,
    end_date: datetime.date,
):
    return (
        db.query(models.Pollutants)
        .filter(
            models.Pollutants.date >= start_date,
            models.Pollutants.date <= end_date,
        )
        .all()
    )

def get_by_city(db: Session, city: str):
    return (
        db.query(models.Pollutants)
        .filter(models.Pollutants.city.ilike(city.strip()))
        .all()
    )

def get_history(db: Session, city: str):
    return (
        db.query(models.Pollutants.date, models.Pollutants.aqi)
        .filter(models.Pollutants.city.ilike(city.strip()))
        .order_by(models.Pollutants.date.desc())
        .all()
    )

def get_average(db: Session, city: str):
    return (
        db.query(
            models.Pollutants.city,
            func.round(func.avg(models.Pollutants.aqi), 2).label(
                "average_aqi"
            ),
        )
        .filter(models.Pollutants.city.ilike(city.strip()))
        .group_by(models.Pollutants.city)
        .first()
    )

def get_best_cities(db: Session):
    return (
        db.query(
            models.Pollutants.city,
            func.round(func.avg(models.Pollutants.aqi), 2).label(
                "average_aqi"
            ),
        )
        .group_by(models.Pollutants.city)
        .order_by("average_aqi")
        .limit(3)
        .all()
    )