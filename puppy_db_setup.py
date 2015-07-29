import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class Shelter(Base):
	__tablename__ = 'shelter'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	address = Column(String(250))
	city = Column(String(80))
	state = Column(String(20))
	zipCode = Column(String(10))
	email = Column(String(80))
	website = Column(String)

	


class Puppy(Base):
	__tablename__ = 'puppy'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	gender = Column(String(6), nullable=False)
	dateOfBirth = Column(Date)
	breed = Column(String(80))
	weight = Column(Numeric(10))
	picture = Column(String)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	shelter = relationship(Shelter)
	profile_id = Column(Integer, ForeignKey('profile.id'))
	profile = relationship(Profile)

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all(engine)

class Profile(Base):
	__tablename__ = 'profile'

	id = Column(Integer, primary_key=True)
	url = Column(String(256), nullable=False)
	description = Column(String(250))
	special_needs = Column(String(250))
