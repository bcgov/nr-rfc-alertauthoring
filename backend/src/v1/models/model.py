# coding: utf-8
from sqlalchemy import \
    Boolean, Column, DateTime, ForeignKey, Integer, String, text, Identity, \
    PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


default_schema = 'py_api'

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema':default_schema}
    # __table_args__ = (
    #     PrimaryKeyConstraint("id", name="user_id_pk"),
    # )

    id = Column(
        Integer,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=1000000,
            cycle=False,
            cache=1,
        ),
        primary_key=True
    )
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    address = relationship("UserAddress", back_populates="user")


# CountyCode = Column('CountyCode', String, ForeignKey('tblCounty.CountyCode'))


class UserAddress(Base):
    __tablename__ = 'user_addresses'
    __table_args__ = {'schema':default_schema}
    # __table_args__ = (
    #     PrimaryKeyConstraint("id", name="useraddress_pk"),
    # )

    id = Column(
        Integer,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=1000000,
            cycle=False,
            cache=1,
        ),
        primary_key=True
    )
    street = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)
    user_id = Column(ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='address')
    
