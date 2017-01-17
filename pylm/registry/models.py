from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, LargeBinary
from pylm.registry.db import Model
from sqlalchemy.orm import relationship
import json


class AdminLog(Model):
    __tablename__ = 'admin_log'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    when = Column(DateTime)


class Admin(Model):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    when = Column(DateTime)
    key = Column(String)

    def __repr__(self):
        return "<Admin {}>".format(self.name)


class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    when = Column(DateTime)
    data = Column(String)
    key = Column(String)
    active = Column(Boolean)
    clusters = relationship("Cluster", back_populates="user")

    def __repr__(self):
        return "<User {}>".format(self.name)

    def dict(self):
        return {
          "name": self.name,
          "when": self.when.isoformat(),
          "data": self.data,
          "key": self.key,
          "active": self.active,
          "clusters": [cluster.key for cluster in self.clusters]
        }

    def json(self):
        return json.dumps(self.dict())


class Cluster(Model):
    __tablename__ = 'clusters'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    when = Column(DateTime)
    description = Column(String)
    status = Column(LargeBinary)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="clusters")