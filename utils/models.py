import datetime
from sqlalchemy import (Column, Integer, DateTime, JSON, String, ForeignKey)
from utils.database import db


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    telegram_id = Column(Integer, default=0)
    registation_date = Column(DateTime, default=datetime.datetime.now())

class Files(db.Model):
    __tablename__ = "available_files"
    id = Column(Integer, primary_key=True)
    file_path = Column(String, default="")
    file = Column(JSON, default=lambda: {})

class Request_history(db.Model):
    __tablename__ = "request_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), default=0)
    request = Column(String, default="")