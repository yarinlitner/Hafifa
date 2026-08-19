import csv
from io import StringIO

from sqlalchemy.orm import Session

import models
from calculate_aqi import calculate_aqi
from logger import logger
from tools import parse_csv_row

def process_csv(content: str, filename: str, db: Session):
    csv_reader = csv.reader(StringIO(content))

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
                logger.warning(
                    f"High AQI alert triggered for "
                    f"{city} on {date}: {aqi}"
                )

                alert = models.Alerts(
                    pollutant_id=pollutant.id,
                    date=date,
                    city=city,
                    aqi=aqi,
                )

                db.add(alert)

            inserted_rows += 1

        except ValueError as err:
            logger.warning(
                f"Row {index + 1} skipped in file "
                f"{filename}: {err}"
            )
            skipped_rows.append(index + 1)

    db.commit()

    logger.info(
        f"Upload complete. Inserted: {inserted_rows}, "
        f"Skipped: {len(skipped_rows)}"
    )

    return {
        "message": "Upload completed",
        "inserted_rows": inserted_rows,
        "skipped_rows": skipped_rows,
    }