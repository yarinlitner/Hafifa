import datetime

from pydantic import BaseModel, ConfigDict


class PollutantCreate(BaseModel):
    date: datetime.date
    city: str
    pm25: float
    no2: float
    co2: float


class PollutantsBase(PollutantCreate):
    id: int
    aqi: float

    model_config = ConfigDict(from_attributes=True)


class AQIHistoryResponse(BaseModel):
    date: datetime.date
    aqi: float

    model_config = ConfigDict(from_attributes=True)


class CityAQIResponse(BaseModel):
    city: str
    aqi: float
    date: datetime.date | None = None

    model_config = ConfigDict(from_attributes=True)


class CityAQIAverageResponse(BaseModel):
    city: str
    average_aqi: float

    model_config = ConfigDict(from_attributes=True)