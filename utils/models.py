import datetime

from sqlalchemy import (Column, Integer, DateTime, String, ForeignKey)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from utils.database import db


class Document(db.Model):
    __tablename__ = "documents"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document = Column(String(300))

    fields_metadata = db.Column(JSONB, nullable=False, server_default="{}")

    def __repr__(self):
        return f"{self.id}, {self.user_id}, {self.document}"


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    telegram_id = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.datetime.now())

    documents = relationship(Document, backref="users")


class Request_history(db.Model):
    __tablename__ = "request_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=0)
    request = Column(String, default="")
