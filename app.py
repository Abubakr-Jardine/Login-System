from flask import Flask, request,url_for, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import pyotp
import qrcode
import io
import base64

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    password_hash = db.Column(db.String(255))
    otp_secret = db.Column(db.String(32))
    otp_enabled = db.Column(db.Boolean, default=False)

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
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password_hash, request.form["password"]):
            if user.otp_enabled:
                session["pending_user_id"] = user.id
                return redirect(url_for("verify_2fa"))
            else:
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)

@app.route("/enable-2fa")
def enable_2fa():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.otp_secret:
        user.otp_secret = pyotp.random_base32()
        db.session.commit()

    uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(
        name=user.username, issuer_name="YourAppName"
    )
 
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render_template("enable_2fa.html", qr_b64=qr_b64)

@app.route("/confirm-2fa", methods=["POST"])
def confirm_2fa():
    user = User.query.get(session["user_id"])
    totp = pyotp.TOTP(user.otp_secret)

    if totp.verify(request.form["code"]):
        user.otp_enabled = True
        db.session.commit()
        flash("Two-factor authentication enabled.")
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid code. Try again.")
        return redirect(url_for("enable_2fa"))

@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if "pending_user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["pending_user_id"])
    totp = pyotp.TOTP(user.otp_secret)

    if request.method == "POST":
        if totp.verify(request.form["code"]):
            session["user_id"] = user.id
            session.pop("pending_user_id")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid code.")

    return render_template("verify_2fa.html")