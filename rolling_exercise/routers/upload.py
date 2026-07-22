import csv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from calculate_aqi import calculate_aqi
from database import SessionLocal, get_db
from logger import logger
from tools import parse_csv_row

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=schemas.UploadResponse)
def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith(".csv"):
        logger.warning(f"Failed upload attempt with invalid file: {file.filename}")
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    logger.info(f"Processing CSV file upload: {file.filename}")
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
                logger.warning(f"High AQI alert triggered for {city} on {date}: {aqi}")
                alert = models.Alerts(
                    pollutant_id=pollutant.id,
                    date=date,
                    city=city,
                    aqi=aqi,
                )
                db.add(alert)

            inserted_rows += 1
        except ValueError as err:
            logger.warning(f"Row {index + 1} skipped in file {file.filename}: {err}")
            skipped_rows.append(index + 1)

    db.commit()
    logger.info(f"Upload complete. Inserted: {inserted_rows}, Skipped: {len(skipped_rows)}")

    return {
        "message": "Upload completed",
        "inserted_rows": inserted_rows,
        "skipped_rows": skipped_rows,
    }