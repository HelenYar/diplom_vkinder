import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from config import sql_name
from psycopg2 import OperationalError

Base = declarative_base()

class Users(Base):
    __tablename__ = 'USER'
    Id_user = sq.Column(sq.Integer, unique=True)
    LastName = sq.Column(sq.String, nullable=False)
    FirstName = sq.Column(sq.String, nullable=False)
    Age = sq.Column(sq.Integer, nullable=False)
    City = sq.Column(sq.String, nullable=False)
    id = sq.Column(sq.Integer, primary_key=True)
    VARIANT = relationship('Variants')

    def __init__(self, user_id, user_last_name, user_first_name, user_age, user_city):
        self.Id_user = user_id
        self.LastName = user_last_name
        self.FirstName = user_first_name
        self.Age = user_age
        self.City = user_city

class Variants(Base):
    __tablename__ = 'VARIANT'
    c_Id = sq.Column(sq.Integer, unique=True)
    LastName = sq.Column(sq.String, nullable=False)
    FirstName = sq.Column(sq.String, nullable=False)
    PersonUrl = sq.Column(sq.String, nullable=False)
    Age = sq.Column(sq.Integer, nullable=False)
    City = sq.Column(sq.String, nullable=False)
    User_id = sq.Column(sq.Integer, sq.ForeignKey('USER.Id_user'))
    id = sq.Column(sq.Integer, primary_key=True)
    PHOTO = relationship('Photos')

    def __init__(self, c_id, c_last_name, c_first_name, c_link, c_age, c_city, c_user_id):
        self.c_Id = c_id
        self.LastName = c_last_name
        self.FirstName = c_first_name
        self.PersonUrl = c_link
        self.Age = c_age
        self.City = c_city
        self.User_id = c_user_id


class Photos(Base):
    __tablename__ = 'PHOTO'
    PhotosUrl = sq.Column(sq.String, nullable=False)
    Var_id = sq.Column(sq.Integer, sq.ForeignKey('VARIANT.c_Id'))
    Id = sq.Column(sq.Integer, primary_key=True)

    def __init__(self, photo,  photo_owner_id):
        self.PhotosUrl = photo
        self.Var_id = photo_owner_id


def create_db(sql_name):
    engine = sq.create_engine(sql_name)
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return session


def clear_db(sql_name):
    engine = sq.create_engine(sql_name)
    connection = engine.connect()
    delete_list = ("PHOTO", 'VARIANT', 'USER')
    for entry in delete_list:
        query_string = f"""DELETE FROM {entry};"""
        connection.execute(query_string)


