from sqlalchemy import Column, Integer, String, DateTime
from pylm.registry.db import Model


class AdminLog(Model):
    __tablename__ = 'admin_log'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    when = Column(DateTime)


class AdminProfile(Model):
    __tablename__ = 'admin_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    when = Column(DateTime)
    key = Column(String)

    def __repr__(self):
        return "<Admin {}>".format(self.name)


class UserProfile(Model):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    when = Column(DateTime)
    data = Column(String)
    key = Column(String)

    def __repr__(self):
        return "<User {}>".format(self.name)
