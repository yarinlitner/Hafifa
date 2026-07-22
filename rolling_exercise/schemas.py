import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PollutantCreate(BaseModel):
    """Schema for validating raw pollutant input data."""
    date: datetime.date
    city: str
    pm25: int
    no2: int
    co2: int

class PollutantsBase(PollutantCreate):
    """Full database record schema for pollutants."""
    id: int
    aqi: int

    model_config = ConfigDict(from_attributes=True)

class AlertsBase(BaseModel):
    """Full database record schema for alerts (AQI > 300)."""
    id: int
    pollutant_id: int
    date: datetime.date
    city: str
    aqi: int

    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    """Response returned after processing a CSV upload."""
    message: str
    inserted_rows: int
    skipped_rows: list[int]

class AQIHistoryResponse(BaseModel):
    """Used for returning date + AQI entries for history queries."""
    date: datetime.date
    aqi: int

    model_config = ConfigDict(from_attributes=True)

class CityAQIResponse(BaseModel):
    """Used for returning a city's current AQI value."""
    city: str
    aqi: int
    date: Optional[datetime.date] = None

    model_config = ConfigDict(from_attributes=True)

class CityAQIAverageResponse(BaseModel):
    """Used for returning average AQI calculations."""
    city: str
    average_aqi: float

    model_config = ConfigDict(from_attributes=True)