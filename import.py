import csv
import os

from flask import Flask, render_template, request
from book.model import *

app = Flask(__name__)

# sqlalchemy init and Check for environment variable
if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] ="postgres://xcnhprolmjsfye:4c46c46015f74d72337667afdbaaa0632951292cc55bbde2e7b0d124efd29e76@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/devprdb0tctod0"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open("books.csv")
    csvreader = csv.reader(f)
    next(csvreader) #skip header
    for isbn, title, author, year in csvreader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added book:  {isbn}: {title} written by {author} in {year}.")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
