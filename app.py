from flask import Flask, request,url_for, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    password_hash = db.Column(db.String(255))

with app.app_context():
    db.create_all()

limiter = Limiter(get_remote_address, app= app, default_limits=[])

@app.route("/",methods = ["POST","GET"])
def index():
    if request.method == "POST":
        if request.form.get("login") == "Login":
            return redirect(url_for("login"))
        elif request.form.get("register") == "Register":
            return redirect(url_for("register"))
    return render_template("index.html")

@app.route("/register", methods = ["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash= hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created. You may now login.")

        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods = ["POST","GET"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username= username).first()

        if user:
            if check_password_hash(user.password_hash,password):
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
            else:
                flash("Password")
                return redirect(url_for("login"))
        else:
            flash("Username")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard", methods = ["GET"])
def dashboard():
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("login"))
    return render_template("dashboard.html")