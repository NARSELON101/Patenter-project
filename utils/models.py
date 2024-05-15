import datetime

from sqlalchemy import (Column, Integer, DateTime, JSON, String, ForeignKey)
from sqlalchemy.orm import relationship

from utils.database import db


class Documents(db.Model):
    __tablename__ = "documents"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document = Column(String(300))

    user = relationship("User", backref="documents")


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    telegram_id = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.datetime.now())

    documents = relationship(Documents, backref="users")


class Request_history(db.Model):
    __tablename__ = "request_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=0)
    request = Column(String, default="")
