from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "book"
    isbn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class User(db.Model):
    __tablename__ = "usr"
    name = db.Column(db.String, primary_key=True)
    passwd = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)

class Review(db.Model):
    __tablename__ = "review"
    book_isbn = db.Column(db.Integer, db.ForeignKey("book.isbn"), primary_key=True)
    usr_name = db.Column(db.String, db.ForeignKey("usr.name"), primary_key=True)
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
