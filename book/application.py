import os

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *


app = Flask(__name__)

# Check for database_url environment variable and init sqlalchemy environmen
if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] ="postgres://xcnhprolmjsfye:4c46c46015f74d72337667afdbaaa0632951292cc55bbde2e7b0d124efd29e76@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/devprdb0tctod0"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# To enable session
app.secret_key = 'super secret key for book app'




# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Index
@app.route("/")
def index():
    return render_template("index.html")


#Show registration form
@app.route("/signup")
def signup():
    return render_template("registration.html")

#Registration
@app.route("/registration", methods=["POST"])
def registration():
    """Register a reader."""
    # Get form information.
    try:
        fullname = request.form.get("fullname")
        name     = request.form.get("name")
        pwd      = request.form.get("pwd")
    except ValueError:
            return render_template("error.html", message="Invalid data")

    if not fullname or not name or not pwd:
        return render_template("error.html", message="Not empty data allowed")

    # Not previous user registed
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

@app.route('/signin')
def signin():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login():
    """Login a reader."""
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
    name = session['user_name']
    session.pop('user_name', None)
    return render_template("success.html", message= f"{name} logged out")
