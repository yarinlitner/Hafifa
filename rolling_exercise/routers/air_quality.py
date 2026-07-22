import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, get_db
from logger import logger

router = APIRouter(prefix="/air-quality", tags=["Air Quality"])

@router.get("/date", response_model=list[schemas.PollutantsBase])
def get_air_quality_by_date(
    start_date: datetime.date,
    end_date: datetime.date,
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

    logger.info(f"Querying air quality from {start_date} to {end_date}")

    return db.query(models.Pollutants).filter(
        models.Pollutants.date >= start_date,
        models.Pollutants.date <= end_date
    ).all()


@router.get("/city", response_model=list[schemas.PollutantsBase])
def get_air_quality_by_city(city: str, db: Session = Depends(get_db)):
    logger.info(f"Querying air quality data for city: {city}")
    records = db.query(models.Pollutants).filter(
        models.Pollutants.city.ilike(city.strip())
    ).all()

    return records


@router.get("/history", response_model=list[schemas.AQIHistoryResponse])
def get_city_aqi_history(city: str, db: Session = Depends(get_db)):
    logger.info(f"Querying AQI history for city: {city}")
    result = (
        db.query(models.Pollutants.date, models.Pollutants.aqi)
        .filter(models.Pollutants.city.ilike(city.strip()))
        .order_by(models.Pollutants.date.desc())
        .all()
    )

    return result


@router.get("/average", response_model=schemas.CityAQIAverageResponse)
def get_city_aqi_average(city: str, db: Session = Depends(get_db)):
    logger.info(f"Calculating AQI average for city: {city}")
    result = (
        db.query(models.Pollutants.city,
                 func.round(func.avg(models.Pollutants.aqi), 2).label("average_aqi")
                )
                .filter(models.Pollutants.city.ilike(city.strip()))
                .group_by(models.Pollutants.city)
                .first()
    )

    return result


@router.get("/best-cities", response_model=list[schemas.CityAQIAverageResponse])
def get_best_cities(db: Session = Depends(get_db)):
    logger.info("Querying best cities by average AQI")
    results = (
        db.query(
            models.Pollutants.city,
            func.round(func.avg(models.Pollutants.aqi), 2).label("average_aqi")
        )
        .group_by(models.Pollutants.city)
        .order_by("average_aqi")
        .limit(3)
        .all()
    )

    return results