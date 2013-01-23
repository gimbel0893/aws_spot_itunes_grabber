import datetime

from basesqlalchemy import Base
from sqlalchemy import (
        Column,
        Integer,
        String,
        DateTime,
    )


class GrabberLog(Base):

    __tablename__ = 'grabber_logs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    queries = Column(Integer)
    results = Column(Integer)
    unique_ids = Column(Integer)
    db_adds = Column(Integer)
    exceptions = Column(Integer)
    created = Column(DateTime)

    def __init__(self, id=None, queries=None, results=None, unique_ids=None,
                 db_adds=None, exceptions=None, created=None):
        self.id = id
        self.queries = queries
        self.results = results
        self.unique_ids = unique_ids
        self.db_adds = db_adds
        self.exceptions = exceptions
        self.created = created or datetime.datetime.utcnow()

    def init(self, stat):
        self.queries = stat.total_queries
        self.results = stat.total_results
        self.unique_ids = len(stat.ids)
        self.db_adds = stat.total_db_adds
        self.exceptions = stat.total_exceptions
        return self
