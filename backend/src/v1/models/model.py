# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata




class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'py_api'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('py_api.user_id_seq'::regclass)"))
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)


class UserAddress(Base):
    __tablename__ = 'user_addresses'
    __table_args__ = {'schema': 'py_api'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('py_api.user_addresses_id_seq'::regclass)"))
    street = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)
    user_id = Column(ForeignKey('py_api.users.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')
