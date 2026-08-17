import datetime
import logging
from unittest.mock import MagicMock
import models

def test_get_air_quality_date_range(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_record = models.Pollutants(
        id=1, date=datetime.date(2026, 1, 1), city="Haifa", pm25=10, no2=20, co2=30, aqi=50
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_record]

    response = client.get("/air-quality/date?start_date=2026-01-01&end_date=2026-01-02")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["city"] == "Haifa"

    # Assert log
    assert "Querying air quality from 2026-01-01 to 2026-01-02" in caplog.text

def test_get_air_quality_invalid_dates(client):
    response = client.get("/air-quality/date?start_date=2026-01-10&end_date=2026-01-01")

    assert response.status_code == 400
    assert "start_date cannot be after end_date" in response.json()["detail"]

def test_get_air_quality_by_city_found(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_record = models.Pollutants(
        id=1, date=datetime.date(2026, 1, 1), city="Haifa", pm25=10, no2=20, co2=30, aqi=50
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_record]

    response = client.get("/air-quality/city?city=Haifa")

    assert response.status_code == 200
    assert response.json()[0]["city"] == "Haifa"

    # Assert log
    assert "Querying air quality data for city: Haifa" in caplog.text

def test_get_air_quality_by_city_not_found(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_db.query.return_value.filter.return_value.all.return_value = []

    response = client.get("/air-quality/city?city=UnknownCity")

    assert response.status_code == 200
    assert response.json() == []

    # Assert log
    assert "Querying air quality data for city: UnknownCity" in caplog.text

def test_get_city_aqi_history(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    row1 = MagicMock(date=datetime.date(2026, 1, 2), aqi=60)
    row2 = MagicMock(date=datetime.date(2026, 1, 1), aqi=50)

    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [row1, row2]

    response = client.get("/air-quality/history?city=Haifa")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["aqi"] == 60

    # Assert log
    assert "Querying AQI history for city: Haifa" in caplog.text

def test_get_city_aqi_average(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_db.query.return_value.filter.return_value.scalar.return_value = 75.456

    response = client.get("/air-quality/average?city=Haifa")

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Haifa"
    assert data["average_aqi"] == 75.46

    # Assert log
    assert "Calculating AQI average for city: Haifa" in caplog.text

def test_get_best_cities(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_results = [("Haifa", 45.0), ("Tel Aviv", 85.0)]
    mock_db.query.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = mock_results

    response = client.get("/air-quality/best-cities")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["city"] == "Haifa"
    assert data[0]["average_aqi"] == 45.0

    # Assert log
    assert "Querying best cities by average AQI" in caplog.text