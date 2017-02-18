#!/usr/bin/env python
"""Provides Entity Structures from SQL magneto.stanford.edu Database"""

from collections import defaultdict
from datetime import date

from sqlalchemy import BigInteger, Column, Float, Integer, Date, String, text
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

    @staticmethod
    def get_batch(sqlClient, batch_size=30000):
        # metadata around minimum and maximum dates retrieved
        sp_id_prev = -1
        earliest_date = date.max
        latest_date = date.min
        result = defaultdict(list)

        contiguous_block = None

        for i, resInterval60 in enumerate(sqlClient.session.query(ResInterval60) \
            .order_by(ResInterval60.sp_id, ResInterval60.date) \
            .limit(batch_size).all()):
            if earliest_date > resInterval60.date:
                earliest_date = resInterval60.date

            if latest_date < resInterval60.date:
                latest_date = resInterval60.date

            # date metadata
            date_info = [0] * 8
            date_info[resInterval60.date.weekday()] = 1

            # weekend
            if resInterval60.date.weekday() >= 5:
                date_info[7] = 1

            if resInterval60.sp_id != sp_id_prev:
                if contiguous_block is not None:
                    result[resInterval60.sp_id].append(contiguous_block)

                contiguous_block = []

            contiguous_block.append([
                resInterval60.q1,
                resInterval60.q2,
                resInterval60.q3,
                resInterval60.q4,
                resInterval60.q5,
                resInterval60.q6,
                resInterval60.q7,
                resInterval60.q8,
                resInterval60.q9,
                resInterval60.q10,
                resInterval60.q11,
                resInterval60.q12,
                resInterval60.q13,
                resInterval60.q14,
                resInterval60.q15,
                resInterval60.q16,
                resInterval60.q17,
                resInterval60.q18,
                resInterval60.q19,
                resInterval60.q20,
                resInterval60.q21,
                resInterval60.q22,
                resInterval60.q23,
                resInterval60.q24
                ] + date_info)

            sp_id_prev = resInterval60.sp_id

        result[sp_id_prev].append(contiguous_block) # add last block

        return result, earliest_date, latest_date

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

    @staticmethod
    def get_weather(sqlClient, earliest_date, latest_date):
        weather = defaultdict(list)

        for localWeather in sqlClient.session.query(LocalWeather) \
            .from_statement(text("SELECT * FROM local_weather WHERE date>=:earliest_date AND date<=:latest_date ORDER BY date")) \
            .params(earliest_date=earliest_date.isoformat(), latest_date=latest_date.isoformat()) \
            .all():

            weather[localWeather.date.strftime('%Y-%m-%d')].extend([
                    localWeather.TemperatureF,
                    localWeather.Humidity
                ])