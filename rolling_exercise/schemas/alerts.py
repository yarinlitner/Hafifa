import datetime

from pydantic import BaseModel, ConfigDict


class AlertsBase(BaseModel):
    id: int
    pollutant_id: int
    date: datetime.date
    city: str
    aqi: float

    model_config = ConfigDict(from_attributes=True)