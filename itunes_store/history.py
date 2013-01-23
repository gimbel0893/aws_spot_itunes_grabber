import datetime

from basesqlalchemy import Base
from sqlalchemy import (
        Column,
        ForeignKey,
        Enum,
        Integer,
        String,
        DateTime,
    )
from sqlalchemy.orm import relationship

from log import GrabberLog
from game import GrabberGame


class History(Base):

    __tablename__ = 'grabber_game_history'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    type = Column(Enum('VERSION', 'PRICE'))
    log_id = Column(Integer, ForeignKey('grabber_logs.id'))
    game_id = Column(Integer, ForeignKey('grabber_games.game_id'))
    created = Column(DateTime)
    log = relationship('GrabberLog', backref='_history')
    game = relationship('GrabberGame', backref='_history')

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': None}

    def __init__(self, id=None, type=None, log_id=None, game_id=None,
                 created=None):
        self.id = id
        self.type = type
        self.log_id = log_id
        self.game_id = game_id
        self.created = created

    def create(self, stp_update, game_id, log_id):
        self.log_id = log_id
        self.game_id = game_id
        self.created = stp_update.change_date
        return self

class Version(History):

    __tablename__ = 'grabber_game_versions'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, ForeignKey('grabber_game_history.id'),
                primary_key=True, autoincrement=False)
    version = Column(String(255))

    __mapper_args__ = {'polymorphic_identity': 'VERSION'}

    def __init__(self, id=None, version=None):
        self.id = id
        self.version = version
        if not self.id:
            self.created = datetime.datetime.utcnow()

    def create(self, stp_version, game_id, log_id):
        super(Version, self).create(stp_version, game_id, log_id)
        self.version = stp_version.old_version
        return self

class Price(History):

    __tablename__ = 'grabber_game_prices'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, ForeignKey('grabber_game_history.id'),
                primary_key=True, autoincrement=False)
    price = Column(String(255))

    __mapper_args__ = {'polymorphic_identity': 'PRICE'}

    def __init__(self, id=None, price=None):
        self.id = id
        self.price = price
        if not self.id:
            self.created = datetime.datetime.utcnow()

    def create(self, stp_price, game_id, log_id):
        super(Price, self).create(stp_price, game_id, log_id)
        self.price = stp_price.old_price
        return self
