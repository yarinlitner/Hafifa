import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
from database import get_db
from logger import logger
from services import air_quality

router = APIRouter(
    prefix="/air-quality",
    tags=["Air Quality"],
)

@router.get("/date", response_model=list[schemas.PollutantsBase])
def get_air_quality_by_date(
    start_date: datetime.date,
    end_date: datetime.date,
    db: Session = Depends(get_db),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    logger.info(
        f"Querying air quality from {start_date} to {end_date}"
    )

    return air_quality.get_by_date(db, start_date, end_date)

@router.get("/city", response_model=list[schemas.PollutantsBase])
def get_air_quality_by_city(
    city: str,
    db: Session = Depends(get_db),
):
    logger.info(f"Querying air quality data for city: {city}")

    return air_quality.get_by_city(db, city)

@router.get("/history", response_model=list[schemas.AQIHistoryResponse])
def get_city_aqi_history(
    city: str,
    db: Session = Depends(get_db),
):
    logger.info(f"Querying AQI history for city: {city}")

    return air_quality.get_history(db, city)

@router.get(
    "/average",
    response_model=schemas.CityAQIAverageResponse,
)
def get_city_aqi_average(
    city: str,
    db: Session = Depends(get_db),
):
    logger.info(f"Calculating AQI average for city: {city}")

    return air_quality.get_average(db, city)

@router.get(
    "/best-cities",
    response_model=list[schemas.CityAQIAverageResponse],
)
def get_best_cities(db: Session = Depends(get_db)):
    logger.info("Querying best cities by average AQI")

    return air_quality.get_best_cities(db)