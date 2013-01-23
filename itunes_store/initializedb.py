import transaction
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection

import basesqlalchemy
from basesqlalchemy import DBSession, Base

from game import GrabberGame
from exception import GrabberException
from log import GrabberLog
from history import Version, Price


STP_TABLE_PREFIX = 'pts_'

def main():
    engine = create_engine(basesqlalchemy.CONNECTION_STRING)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    """
    Base.metadata.reflect(engine)
    inspector = reflection.Inspector.from_engine(engine)
    for table in Base.metadata.tables.keys():
        if 'InnoDB' != inspector.get_table_options(table)['mysql_engine']:
            DBSession.execute('ALTER TABLE {} ENGINE = InnoDB'.format(table))
    """

    #with transaction.manager:


if __name__ == '__main__':
    main()
