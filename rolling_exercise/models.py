from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from database import base

class Pollutants(Base):
    __tablename__ = 'pollutants'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    city = Column(String)
    pm25 = Column(Integer)
    no2 = Column(Integer)
    co2 = Column(Integer)
    aqi = Column(Integer)

class Alerts(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    pollutant_id = Column(Integer, ForeignKey("pollutants.id"))
    date = Column(Date)
    city = Column(String)
    aqi = Column(Integer)
