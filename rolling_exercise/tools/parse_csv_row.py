import math
import datetime

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