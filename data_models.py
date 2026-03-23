from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    birth_date = Column(String)
    date_of_death = Column(String)

class Book(db.Model):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String)
    title = Column(String)
    publication_year = Column(String)
    cover = Column(String)
    author_id = Column(Integer)

