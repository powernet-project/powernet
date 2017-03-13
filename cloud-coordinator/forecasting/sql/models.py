#!/usr/bin/env python
"""Provides Entity Structures from SQL magneto.stanford.edu Database"""

from collections import defaultdict
import datetime

from sqlalchemy import BigInteger, Column, Float, Integer, Date, String, text
from sqlalchemy.ext.declarative import declarative_base

import operator
import pdb

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

Base = declarative_base()
multiadd = lambda a,b: map(operator.add, a,b)

AGGREGATE_SIZE = 20

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
        counter = 1
        result = []

        earliest_date = datetime.date.max
        latest_date = datetime.date.min
        aggregate_load_dict = dict()

        for i, resInterval60 in enumerate(sqlClient.session.query(ResInterval60) \
            .order_by(ResInterval60.sp_id, ResInterval60.date) \
            .limit(batch_size).all()):

            if earliest_date > resInterval60.date:
                earliest_date = resInterval60.date

            if latest_date < resInterval60.date:
                latest_date = resInterval60.date

            if resInterval60.sp_id != sp_id_prev and sp_id_prev != -1:
                if counter == AGGREGATE_SIZE:
                    date_prev = datetime.date.min
                    aggregate_load_list = [(k,v) for k, v in aggregate_load_dict.items()]
                    aggregate_load_list.sort()
                    contiguous_block = None

                    for date, load in aggregate_load_list:
                        if date - datetime.timedelta(days=1) > date_prev or aggregate_load_list[-1][0] == date:
                            if contiguous_block is not None:
                                contiguous_block.append(date) #sentinel end date
                                result.append(contiguous_block)

                            contiguous_block = [date] #sentinel start date

                        if contiguous_block is None:
                            contiguous_block = [date]

                        # date metadata
                        date_info = [0] * 8
                        date_info[date.weekday()] = 1

                        # weekend
                        if date.weekday() >= 5:
                            date_info[7] = 1

                        contiguous_block.append(load + date_info)
                        date_prev = date

                    aggregate_load_dict = dict()
                    counter = 1
                else:
                    counter = counter + 1

            if resInterval60.date in aggregate_load_dict:
                aggregate_load_dict[resInterval60.date] = multiadd(aggregate_load_dict[resInterval60.date], [
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
                    ])
            else:
                aggregate_load_dict[resInterval60.date] = [
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
                    ]

            sp_id_prev = resInterval60.sp_id

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
            .from_statement(text("SELECT * FROM local_weather WHERE date>=:earliest_date AND date<=:latest_date ORDER BY zip5, date")) \
            .params(earliest_date=earliest_date.isoformat(), latest_date=latest_date.isoformat()) \
            .all():

            weather[localWeather.date.strftime('%Y-%m-%d')].extend([
                    localWeather.TemperatureF,
                    localWeather.Humidity
                ])

        return weather