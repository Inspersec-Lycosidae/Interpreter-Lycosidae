# models.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, ForeignKey, CheckConstraint, UniqueConstraint, SmallInteger
)
from sqlalchemy.orm import relationship, declarative_base
Base = declarative_base()

######################################################################
##### Uses SqlAlchemy bases for static objects; referenced in DB #####
######################################################################

#Default generic user table
#Use for reference on developing new tables
class User(Base):
    __tablename__ = 'user'

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(60), nullable=False, unique=True)
    email = Column(String(45), nullable=False, unique=True)
    password256 = Column(String(256), nullable=False)