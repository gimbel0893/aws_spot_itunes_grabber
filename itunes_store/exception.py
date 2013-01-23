from basesqlalchemy import Base
from sqlalchemy import (
        Column,
        ForeignKey,
        Integer,
        String,
        Text,
    )
from sqlalchemy.orm import relationship, backref

from log import GrabberLog


class GrabberException(Base):

    __tablename__ = 'grabber_exceptions'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey('grabber_logs.id'))
    type = Column(String(255))
    message = Column(Text)
    search_term = Column(String(255))
    limit = Column(Integer)
    offset = Column(Integer)
    iteration = Column(Integer)
    log = relationship('GrabberLog', backref='_exceptions')

    def __init__(self, id=None, log_id=None, type=None, message=None,
                 search_term=None, limit=None, offset=None, iteration=None,
                 log=None):
        self.id = id
        self.log_id = log_id
        self.type = type
        self.message = message
        self.search_term = search_term
        self.limit = limit
        self.offset = offset
        self.iteration = iteration
        self.log = log
