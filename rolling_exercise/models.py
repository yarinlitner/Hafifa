from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from database import Base

class Pollutants(Base):
    __tablename__ = 'pollutants'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    city = Column(String)
    pm25 = Column(Float)
    no2 = Column(Float)
    co2 = Column(Float)
    aqi = Column(Float)

class Alerts(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    pollutant_id = Column(Integer, ForeignKey("pollutants.id"))
    date = Column(Date)
    city = Column(String)
    aqi = Column(Float)
