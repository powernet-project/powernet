#!/usr/bin/env python
"""Provides SqlClient using SqlAlchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

username = 'powernet'
password = 'netpower'
host = 'localhost'
database = 'powernet'

class SqlClient:
  def __init__(self):
    self.engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.format(username, password, host, database))
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()