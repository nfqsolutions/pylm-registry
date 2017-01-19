from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from pylm.registry.application import configuration


class Handler(object):
    def __init__(self):
        self.engine = create_engine(configuration['DB']['Uri'],
                                    echo=configuration.getboolean('DB', 'Debug'))
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.Model = declarative_base(bind=self.engine)

    def sync_tables(self):
        self.Model.metadata.create_all(self.engine)


# Instances for DB handling
DB = Handler()
Model = DB.Model
