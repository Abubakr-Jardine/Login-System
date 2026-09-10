from flask import Flask, request,url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
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

@app.route("/",methods = ["POST","GET"])
def index():
    if request.method == "POST":
        if request.form.get("action1") == "Login":
            return redirect(url_for("login_page"))
    return render_template("index.html")

@app.route("/login", methods = ["POST","GET"])
def login_page():
    return render_template("login.html")