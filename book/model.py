from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "book"
    isbn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def print_info(self):
        print(f"Isbn: {self.isbn}")
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Year: {self.year}")

class User(db.Model):
    __tablename__ = "usr"
    name = db.Column(db.String, primary_key=True)
    passwd = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)

    def print_info(self):
        print(f"Name: {self.name}")
        print(f"Fullname: {self.fullname}")

    def print_info_ext(self):
        print(f"Name: {self.name}")
        print(f"Passwd: {self.passwd}")
        print(f"Fullname: {self.fullname}")

class Review(db.Model):
    __tablename__ = "review"
    book_isbn = db.Column(db.Integer, db.ForeignKey("book.isbn"), primary_key=True)
    usr_name = db.Column(db.String, db.ForeignKey("usr.name"), primary_key=True)
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def print_info(self):
        print(f"Book_isbn: {self.book_isbn}")
        print(f"Usr_name: {self.usr_name}")
        print(f"Text: {self.text}")
        print(f"Rating: {self.rating}")
