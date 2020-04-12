import os
import requests

from flask import Flask, render_template, jsonify, request, session
from flask_session import Session
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *



app = Flask(__name__)

# Check for database_url environment variable and init sqlalchemy environmen
if os.getenv("DATABASE_URL"):
    database_url = os.getenv("DATABASE_URL")
else:
    database_url = "postgres://xcnhprolmjsfye:4c46c46015f74d72337667afdbaaa0632951292cc55bbde2e7b0d124efd29e76@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/devprdb0tctod0"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Goodreads apikey
GOODREADS_APIKEY="v9UkBJzCMLyRy0ArJ2kIpA"

# To enable session
app.secret_key = 'super secret key for book app'




# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Set up database
engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind=engine))

#Index
@app.route("/")
def index():
    return render_template("index.html")


#Show registration form
@app.route("/showregistrationform")
def showregistrationform():
    """Show registration form """
    try:
        name = session['user_name']
    except KeyError:
        #not logged in - show form
        return render_template("registration.html")

    # Already logged in - Error
    return render_template("error.html", message="Your are already logged in. Your must logout")


#Registration
@app.route("/registration", methods=["POST"])
def registration():
    """Register a user."""

    # Get form information.
    try:
        fullname = request.form.get("fullname")
        name     = request.form.get("name")
        pwd      = request.form.get("pwd")
    except ValueError:
            return render_template("error.html", message="Invalid data")

    if not fullname or not name or not pwd:
        return render_template("error.html", message="Not empty data allowed")

    # Not previous user.name registed in db
    user = User.query.get(name);
    if user is not None:
        return render_template("error.html", message="There's already a user with this name. Choose another name, please.")

    # Add User into DB
    user = User(name=name, passwd=pwd, fullname=fullname)
    db.add(user)
    db.commit()

    # Loggin in session
    session['user_name']=user.name;

    #output
    return render_template("success.html", message= f"{user.name} registrated.")

@app.route('/showloginform')
def showloginform():
    """Show login form."""

    #Check if is logged in
    try:
        name = session['user_name']
    except KeyError:
        # Not logged in - show login form
        return render_template("login.html")

    return render_template("error.html", message="Your are already logged in. Your must logout")




@app.route('/login', methods=["POST"])
def login():
    """Login a user"""
    # Get form information.
    try:
        name     = request.form.get("name")
        passwd      = request.form.get("pwd")
    except ValueError:
            return render_template("error.html", message="Invalid data")

    if not name or not passwd:
        return render_template("error.html", message="Not empty data allowed")

    # Not previous user registed
    #user = User.query.filter(and_(name==name,passwd==passwd)).first()
    #user =  User.query.get(name).filter_by(passwd=passwd)).first()
    user = User.query.get(name)
    if user is None:
        return render_template("error.html", message="Try another Nick")

    if not user.passwd == passwd:
        return render_template("success.html", message= "Invalid passwd")

    session['user_name']=user.name;

    #if 'visits' in session:
    #    session['visits'] = session.get('visits') + 1  # reading and updating session data
    #else:
    #    session['visits'] = 1 # setting session data
    #return render_template("success.html", message= f"{session.get('visits'), {session.get(user.name)},}   num de visitas.")


    return render_template("success.html", message= f"{session.get('user_name')} logged in")

@app.route('/logout', methods=["GET","POST"])
def logout():
    """Logout a user"""
    try:
        name = session['user_name']
    except KeyError:
        return render_template("error.html", message="Your are not logged in")

    session.pop('user_name', None)
    return render_template("success.html", message= f"{name} logged out")

@app.route('/showsearchbookform', methods=["GET","POST"])
def showsearchbookform():
    """Show Search book form"""
    # Check if is logged in
    try:
        name = session['user_name']
    except KeyError:
        return render_template("error.html", message="Your must be logged in")

    # Show showsearchbookform
    return render_template("bookform.html")

@app.route('/booksearch', methods=["POST"])
def booksearch():
    """Search a book"""
    # Check if is logged in
    try:
        name = session['user_name']
    except KeyError:
        return render_template("error.html", message="Your must be logged in")

    # Get form info
    try:
        isbn     = request.form.get("isbn")
        title    = request.form.get("title")
        author   = request.form.get("author")
    except ValueError:
            return render_template("error.html", message="Invalid data")

    if not isbn and not title and not author:
        return render_template("error.html", message="Your must insert, at least, part of a data.");

    # Search
    books = Book.query.filter(and_(Book.isbn.like(f"%{isbn}%"), Book.title.like(f"%{title}%"), Book.author.like(f"%{author}%"))).all()

    if not books:
        return render_template("error.html", message=f"Form data: .{isbn}.{title}.{author}. No Match");

    return render_template("books.html",books=books)


@app.route("/books/<string:isbn>", methods=["GET","POST"])
def book(isbn):
    """List details about a book"""

    # Make sure book exists.
    book = Book.query.get(isbn)
    if book is None:
        return render_template("error.html", message="No such book.")

    # Get all reviews.
    reviews=book.reviews

    # Get goodreads info
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_APIKEY, "isbns": isbn})
    if res.status_code == 200:
        goodreadsbook=res.json()["books"][0]
    else:
        goodreadsbook=None

    return render_template("book.html", book=book, reviews=reviews,goodreadsbook=goodreadsbook)

@app.route("/books/<string:isbn>/reviewadd", methods=["POST"])
def reviewadd(isbn):
    """List details about a book"""

    # Make sure book exists.
    book = Book.query.get(isbn)
    if book is None:
        return render_template("error.html", message="No such book.")

    # Get session name
    name = session['user_name']

    # Get form info
    try:
        text   = request.form.get("text")
        rating = request.form.get("rating")
    except ValueError:
            return render_template("error.html", message="Invalid data")

    if not text or not rating:
        return render_template("error.html", message="Please, complete all data");

    #Check no previous review for this users and this book
    previousreview = Review.query.filter(and_(Review.book_isbn==isbn,Review.user_name==name)).first()
    if previousreview:
        return render_template("error.html", message="You have already a review for this book");

    book.add_review(name,text,rating)
    reviews=book.reviews

    # Get goodreads info
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_APIKEY, "isbns": isbn})
    if res.status_code == 200:
        goodreadsbook=res.json()["books"][0]
    else:
        goodreadsbook=None

    return render_template("book.html", book=book, reviews=reviews,goodreadsbook=goodreadsbook)

@app.route("/api/<string:isbn>")
def api_book(isbn):
    """Return details about a book."""

    # Make sure book exists.
    book = Book.query.get(isbn)
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422

    # Get goodreads info
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_APIKEY, "isbns": isbn})

    #return json object
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count" :res.json()["books"][0].get("work_ratings_count"),
            "average_score": float(res.json()["books"][0].get("average_rating"))
    })
