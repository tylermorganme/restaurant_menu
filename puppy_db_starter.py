from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from puppy_db_setup import Base, Puppy, Shelter

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# puppies = session.query(Puppy).all()
puppies = session.query(func.count(Puppy.id)).group_by(Puppy.shelter_id).all()
for puppy in puppies:
    print puppy
