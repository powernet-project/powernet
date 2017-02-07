#!/usr/bin/env python
"""Provides Entity Structures from SQL magneto.stanford.edu Database"""

from sqlalchemy import BigInteger, Column, Float, Integer, Date, String
from sqlalchemy.ext.declarative import declarative_base

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

Base = declarative_base()

class ResInterval60(Base):
    __tablename__ = 'res_interval_60'

    id = Column(Integer, primary_key=True)
    sp_id = Column(BigInteger)
    sa_id = Column(BigInteger)
    date = Column(Date)
    date_char = Column(String(10))
    unitmeas = Column(String(5))
    q1 = Column(Float)
    q2 = Column(Float)
    q3 = Column(Float)
    q4 = Column(Float)
    q5 = Column(Float)
    q6 = Column(Float)
    q7 = Column(Float)
    q8 = Column(Float)
    q9 = Column(Float)
    q10 = Column(Float)
    q11 = Column(Float)
    q12 = Column(Float)
    q13 = Column(Float)
    q14 = Column(Float)
    q15 = Column(Float)
    q16 = Column(Float)
    q17 = Column(Float)
    q18 = Column(Float)
    q19 = Column(Float)
    q20 = Column(Float)
    q21 = Column(Float)
    q22 = Column(Float)
    q23 = Column(Float)
    q24 = Column(Float)

class LocalWeather(Base):
    __tablename__ = 'local_weather'

    id = Column(Integer, primary_key=True)
    zip5 = Column(Integer)
    TemperatureF = Column(Float)
    DewpointF = Column(Float)
    Pressure = Column(Float)
    WindSpeed = Column(Float)
    Humidity = Column(Float)
    Clouds = Column(String)
    HourlyPrecip = Column(Float)
    SolarRadiation = Column(Float)
    date = Column(Date)
