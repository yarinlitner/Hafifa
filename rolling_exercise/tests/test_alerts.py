import datetime
import logging
import models


def test_get_all_alerts(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_alert = models.Alerts(
        id=1, pollutant_id=10, date=datetime.date(2026, 1, 1), city="Haifa", aqi=350
    )
    mock_db.query.return_value.all.return_value = [mock_alert]

    response = client.get("/alerts")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["aqi"] == 350

    # Assert log
    assert "Retrieving all alerts" in caplog.text


def test_get_alerts_by_date(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_alert = models.Alerts(
        id=1, pollutant_id=10, date=datetime.date(2026, 1, 1), city="Haifa", aqi=350
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_alert]

    response = client.get("/alerts/date?date=2026-01-01")

    assert response.status_code == 200
    assert response.json()[0]["city"] == "Haifa"

    # Assert log
    assert "Retrieving alerts for date: 2026-01-01" in caplog.text


def test_get_alerts_by_city(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    mock_db.query.return_value.filter.return_value.all.return_value = []

    response = client.get("/alerts/city?city=CleanCity")

    assert response.status_code == 200
    assert response.json() == []

    # Assert log
    assert "Retrieving alerts for city: CleanCity" in caplog.text