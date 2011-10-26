from db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
import datetime

class Room(Base):
  __tablename__ = 'rooms'

  id = Column(Integer, primary_key=True)
  name = Column(String)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "<Room('%s')>" % (self.name)

class Message(Base):
  __tablename__ = 'messages'

  id = Column(Integer, primary_key=True)
  message = Column(String)
  dt = Column(DateTime)
  room_id = Column(Integer, ForeignKey('rooms.id'))
  room = relationship("Room", backref=backref('messages', order_by=dt))

  def __init__(self, message):
    self.message = message
    self.dt = datetime.datetime.now()

  def __repr__(self):
    return "<Message('%s','%s')>" % (self.message, self.dt)
