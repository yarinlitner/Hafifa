import csv
import datetime
import math
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from calculate_aqi import calculate_aqi
from database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class PollutantsBase(BaseModel):
    id: int
    date: datetime.date
    city: str
    pm25: float
    no2: float
    co2: float
    aqi: float


class AlertsBase(BaseModel):
    id: int
    pollutant_id: int
    date: datetime.date
    city: str
    aqi: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def parse_csv_row(row: list[str]) -> tuple[datetime.date, str, float, float, float]:
    if len(row) != 5:
        raise ValueError("Row must contain exactly 5 values")

    date = datetime.date.fromisoformat(row[0].strip())
    city = row[1].strip()
    pm25 = float(row[2].strip())
    no2 = float(row[3].strip())
    co2 = float(row[4].strip())

    if math.isnan(pm25) or math.isnan(no2) or math.isnan(co2):
        raise ValueError("Pollutant values cannot be NaN")

    return date, city, pm25, no2, co2


@app.post("/upload")
def upload(file: UploadFile = File(...), db: db_dependency = None):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    content = file.file.read().decode("utf-8")
    csv_reader = csv.reader(content.splitlines())

    inserted_rows = 0
    skipped_rows = []

    for index, row in enumerate(csv_reader):
        if index == 0:
            continue

        try:
            date, city, pm25, no2, co2 = parse_csv_row(row)
            aqi, _ = calculate_aqi(pm25, no2, co2)

            pollutant = models.Pollutants(
                date=date,
                city=city,
                pm25=pm25,
                no2=no2,
                co2=co2,
                aqi=aqi,
            )
            db.add(pollutant)
            db.flush()

            if aqi > 300:
                alert = models.Alerts(
                    pollutant_id=pollutant.id,
                    date=date,
                    city=city,
                    aqi=aqi,
                )
                db.add(alert)

            inserted_rows += 1
        except ValueError:
            skipped_rows.append(index + 1)

    db.commit()

    return {
        "message": "Upload completed",
        "inserted_rows": inserted_rows,
        "skipped_rows": skipped_rows,
    }
