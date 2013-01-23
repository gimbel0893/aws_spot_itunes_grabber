from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import create_engine

CONNECTION_STRING = \
    'mysql+mysqldb://stp:stp@127.0.0.1/stp?charset=utf8'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

engine = create_engine(CONNECTION_STRING)
DBSession.configure(bind=engine)
