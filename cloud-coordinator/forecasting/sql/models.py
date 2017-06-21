#!/usr/bin/env python
"""Provides Entity Structures from Sql magneto.stanford.edu Database"""

from collections import defaultdict
from datetime import date, timedelta
import holidays

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
        us_ca_holidays = holidays.US(state='CA')

        # metadata around minimum and maximum dates retrieved
        sp_id_prev = -1
        date_prev = date.min
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

            # weekend or holiday
            if resInterval60.date.weekday() >= 5 or resInterval60.date in us_ca_holidays:
                date_info[7] = 1

            if resInterval60.sp_id != sp_id_prev or \
                resInterval60.date - timedelta(days=1) > date_prev:

                if contiguous_block is not None:
                    contiguous_block.append(resInterval60.date) #sentinel end date
                    result[sp_id_prev].append(contiguous_block)

                contiguous_block = [resInterval60.date] #sentinel start date

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
            date_prev = resInterval60.date

        result[sp_id_prev].append(contiguous_block) # add last block

        return result, earliest_date, latest_date

class ResInterval15(Base):
    __tablename__ = 'res_interval_15'

    id = Column(Integer, primary_key=True)
    spid = Column(BigInteger)
    date = Column(Date)
    unitmeas = Column(Integer)
    flow = Column(String(5))
    qkw1=Column(Float)
    qkw2=Column(Float)
    qkw3=Column(Float)
    qkw4=Column(Float)
    qkw5=Column(Float)
    qkw6=Column(Float)
    qkw7=Column(Float)
    qkw8=Column(Float)
    qkw9=Column(Float)
    qkw10=Column(Float)
    qkw11=Column(Float)
    qkw12=Column(Float)
    qkw13=Column(Float)
    qkw14=Column(Float)
    qkw15=Column(Float)
    qkw16=Column(Float)
    qkw17=Column(Float)
    qkw18=Column(Float)
    qkw19=Column(Float)
    qkw20=Column(Float)
    qkw21=Column(Float)
    qkw22=Column(Float)
    qkw23=Column(Float)
    qkw24=Column(Float)
    qkw25=Column(Float)
    qkw26=Column(Float)
    qkw27=Column(Float)
    qkw28=Column(Float)
    qkw29=Column(Float)
    qkw30=Column(Float)
    qkw31=Column(Float)
    qkw32=Column(Float)
    qkw33=Column(Float)
    qkw34=Column(Float)
    qkw35=Column(Float)
    qkw36=Column(Float)
    qkw37=Column(Float)
    qkw38=Column(Float)
    qkw39=Column(Float)
    qkw40=Column(Float)
    qkw41=Column(Float)
    qkw42=Column(Float)
    qkw43=Column(Float)
    qkw44=Column(Float)
    qkw45=Column(Float)
    qkw46=Column(Float)
    qkw47=Column(Float)
    qkw48=Column(Float)
    qkw49=Column(Float)
    qkw50=Column(Float)
    qkw51=Column(Float)
    qkw52=Column(Float)
    qkw53=Column(Float)
    qkw54=Column(Float)
    qkw55=Column(Float)
    qkw56=Column(Float)
    qkw57=Column(Float)
    qkw58=Column(Float)
    qkw59=Column(Float)
    qkw60=Column(Float)
    qkw61=Column(Float)
    qkw62=Column(Float)
    qkw63=Column(Float)
    qkw64=Column(Float)
    qkw65=Column(Float)
    qkw66=Column(Float)
    qkw67=Column(Float)
    qkw68=Column(Float)
    qkw69=Column(Float)
    qkw70=Column(Float)
    qkw71=Column(Float)
    qkw72=Column(Float)
    qkw73=Column(Float)
    qkw74=Column(Float)
    qkw75=Column(Float)
    qkw76=Column(Float)
    qkw77=Column(Float)
    qkw78=Column(Float)
    qkw79=Column(Float)
    qkw80=Column(Float)
    qkw81=Column(Float)
    qkw82=Column(Float)
    qkw83=Column(Float)
    qkw84=Column(Float)
    qkw85=Column(Float)
    qkw86=Column(Float)
    qkw87=Column(Float)
    qkw88=Column(Float)
    qkw89=Column(Float)
    qkw90=Column(Float)
    qkw91=Column(Float)
    qkw92=Column(Float)
    qkw93=Column(Float)
    qkw94=Column(Float)
    qkw95=Column(Float)
    qkw96=Column(Float)

    @staticmethod
    def get_batch(sqlClient, batch_size=30000):
        # metadata around minimum and maximum dates retrieved
        sp_id_prev = -1
        date_prev = date.min
        earliest_date = date.max
        latest_date = date.min
        result = defaultdict(list)

        contiguous_block = None

        for i, resInterval15 in enumerate(sqlClient.session.query(ResInterval15) \
            .order_by(ResInterval15.spid, ResInterval15.date) \
            .limit(batch_size).all()):
            if earliest_date > ResInterval15.date:
                earliest_date = ResInterval15.date

            if latest_date < ResInterval15.date:
                latest_date = ResInterval15.date

            # date metadata
            date_info = [0] * 8
            date_info[ResInterval15.date.weekday()] = 1

            # weekend
            if ResInterval15.date.weekday() >= 5:
                date_info[7] = 1

            if ResInterval15.sp_id != sp_id_prev or \
                ResInterval15.date - timedelta(days=1) > date_prev:

                if contiguous_block is not None:
                    contiguous_block.append(ResInterval15.date) #sentinel end date
                    result[sp_id_prev].append(contiguous_block)

                contiguous_block = [ResInterval15.date] #sentinel start date

            contiguous_block.append([
                ResInterval15.qkw1,
                ResInterval15.qkw2,
                ResInterval15.qkw3,
                ResInterval15.qkw4,
                ResInterval15.qkw5,
                ResInterval15.qkw6,
                ResInterval15.qkw7,
                ResInterval15.qkw8,
                ResInterval15.qkw9,
                ResInterval15.qkw10,
                ResInterval15.qkw11,
                ResInterval15.qkw12,
                ResInterval15.qkw13,
                ResInterval15.qkw14,
                ResInterval15.qkw15,
                ResInterval15.qkw16,
                ResInterval15.qkw17,
                ResInterval15.qkw18,
                ResInterval15.qkw19,
                ResInterval15.qkw20,
                ResInterval15.qkw21,
                ResInterval15.qkw22,
                ResInterval15.qkw23,
                ResInterval15.qkw24,
                ResInterval15.qkw25,
                ResInterval15.qkw26,
                ResInterval15.qkw27,
                ResInterval15.qkw28,
                ResInterval15.qkw29,
                ResInterval15.qkw30,
                ResInterval15.qkw31,
                ResInterval15.qkw32,
                ResInterval15.qkw33,
                ResInterval15.qkw34,
                ResInterval15.qkw35,
                ResInterval15.qkw36,
                ResInterval15.qkw37,
                ResInterval15.qkw38,
                ResInterval15.qkw39,
                ResInterval15.qkw40,
                ResInterval15.qkw41,
                ResInterval15.qkw42,
                ResInterval15.qkw43,
                ResInterval15.qkw44,
                ResInterval15.qkw45,
                ResInterval15.qkw46,
                ResInterval15.qkw47,
                ResInterval15.qkw48,
                ResInterval15.qkw49,
                ResInterval15.qkw50,
                ResInterval15.qkw51,
                ResInterval15.qkw52,
                ResInterval15.qkw53,
                ResInterval15.qkw54,
                ResInterval15.qkw55,
                ResInterval15.qkw56,
                ResInterval15.qkw57,
                ResInterval15.qkw58,
                ResInterval15.qkw59,
                ResInterval15.qkw60,
                ResInterval15.qkw61,
                ResInterval15.qkw62,
                ResInterval15.qkw63,
                ResInterval15.qkw64,
                ResInterval15.qkw65,
                ResInterval15.qkw66,
                ResInterval15.qkw67,
                ResInterval15.qkw68,
                ResInterval15.qkw69,
                ResInterval15.qkw70,
                ResInterval15.qkw71,
                ResInterval15.qkw72,
                ResInterval15.qkw73,
                ResInterval15.qkw74,
                ResInterval15.qkw75,
                ResInterval15.qkw76,
                ResInterval15.qkw77,
                ResInterval15.qkw78,
                ResInterval15.qkw79,
                ResInterval15.qkw80,
                ResInterval15.qkw81,
                ResInterval15.qkw82,
                ResInterval15.qkw83,
                ResInterval15.qkw84,
                ResInterval15.qkw85,
                ResInterval15.qkw86,
                ResInterval15.qkw87,
                ResInterval15.qkw88,
                ResInterval15.qkw89,
                ResInterval15.qkw90,
                ResInterval15.qkw91,
                ResInterval15.qkw92,
                ResInterval15.qkw93,
                ResInterval15.qkw94,
                ResInterval15.qkw95,
                ResInterval15.qkw96
            ] + date_info)

            sp_id_prev = ResInterval15.spid
            date_prev = ResInterval15.date

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
            .from_statement(text("SELECT * FROM local_weather WHERE date>=:earliest_date AND date<=:latest_date ORDER BY zip5, date")) \
            .params(earliest_date=earliest_date.isoformat(), latest_date=latest_date.isoformat()) \
            .all():

            weather[localWeather.date.strftime('%Y-%m-%d')].extend([
                    localWeather.TemperatureF,
                    localWeather.Humidity
                ])

        return weather