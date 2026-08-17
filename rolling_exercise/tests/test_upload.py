import io
import logging

def test_upload_valid_csv(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    csv_content = (
        "date,city,pm25,no2,co2\n"
        "2026-01-01,Haifa,10.0,20.0,30.0\n"
        "2026-01-02,Tel Aviv,15.0,25.0,35.0\n"
    )
    file = ("data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")

    response = client.post("/upload", files={"file": file})

    assert response.status_code == 200
    data = response.json()
    assert data["inserted_rows"] == 2
    assert data["skipped_rows"] == []
    
    # Verify mock database interactions
    assert mock_db.add.call_count == 2
    assert mock_db.commit.called

    # Assert log statements
    assert "Processing CSV file upload: data.csv" in caplog.text
    assert "Upload complete. Inserted: 2, Skipped: 0" in caplog.text

def test_upload_high_aqi_adds_alert(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    csv_content = (
        "date,city,pm25,no2,co2\n"
        "2026-01-01,Haifa,300.0,700.0,120.0\n"
    )
    file = ("data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")

    response = client.post("/upload", files={"file": file})

    assert response.status_code == 200
    assert mock_db.add.call_count == 2

    # Assert high AQI alert log
    assert "High AQI alert triggered for Haifa on 2026-01-01" in caplog.text

def test_upload_corrupted_rows_skipped(client, mock_db, caplog):
    caplog.set_level(logging.INFO)
    
    csv_content = (
        "date,city,pm25,no2,co2\n"
        "2026-01-01,Haifa,10.0,20.0,30.0\n"
        "invalid-date,Tel Aviv,15.0,25.0,35.0\n"
    )
    file = ("data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")

    response = client.post("/upload", files={"file": file})

    assert response.status_code == 200
    data = response.json()
    assert data["inserted_rows"] == 1
    assert data["skipped_rows"] == [3]

    # Assert skipped row warning log
    assert "Row 3 skipped in file data.csv" in caplog.text

def test_upload_non_csv_rejected(client, caplog):
    caplog.set_level(logging.WARNING)
    
    file = ("document.pdf", io.BytesIO(b"dummy pdf content"), "application/pdf")

    response = client.post("/upload", files={"file": file})

    assert response.status_code == 400
    assert "Please upload a CSV file" in response.json()["detail"]

    # Assert failed attempt log
    assert "Failed upload attempt with invalid file: document.pdf" in caplog.text