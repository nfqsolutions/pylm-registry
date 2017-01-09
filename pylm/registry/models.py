from sqlalchemy import Column, Integer, String, DateTime
from pylm.registry.db import Model


class AdminProfile(Model):
    __tablename__ = 'admin_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    when = Column(DateTime)
    key = Column(String)

    def __repr__(self):
        return "<Admin {}>".format(self.name)
