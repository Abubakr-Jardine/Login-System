# Secure Login System

A Flask-based login system built to demonstrate practical web security concepts, including password hashing, session management, rate limiting, and two-factor authentication (2FA).

This project was built from the ground up, as a way to learn Flask while applying core cybersecurity principles.

## Features

- User registration and login with hashed passwords (no plaintext storage)
- Session-based authentication using signed cookies
- Two-factor authentication (TOTP) via authenticator apps (Google Authenticator, Authy, etc.)
- Rate limiting on login attempts to slow brute-force attacks
- SQL injection protection via SQLAlchemy's ORM
- Generic authentication error messages to prevent username enumeration

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite, via Flask-SQLAlchemy
- **Auth:** Werkzeug (password hashing), PyOTP (2FA)
- **Rate limiting:** Flask-Limiter
- **Frontend:** HTML, Jinja2 templates, CSS

## Project Structure

```
secure-login-app/
├── app.py
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── enable_2fa.html
│   └── verify_2fa.html
└── instance/
    └── users.db
```

## Setup

```bash
git clone <git@github.com:Abubakr-Jardine/Login-System.git>
cd Login-System
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install flask flask-sqlalchemy werkzeug flask-limiter pyotp qrcode[pil]
flask --app app run
```

Visit `http://127.0.0.1:5000`.

## How It Works

### Registration
A new user submits a username and password. The password is hashed with `werkzeug.security.generate_password_hash` before being stored — the raw password is never saved.

### Login
Credentials are checked against the stored hash with `check_password_hash`. If the account has 2FA enabled, the user is *not* fully authenticated yet — they're redirected to a second verification step before their session is marked as logged in.

### Two-Factor Authentication
Users can enable 2FA from their dashboard. This generates a random secret, displayed as a QR code for scanning into an authenticator app. The user must submit one valid code before 2FA is actually turned on, to avoid a broken setup locking them out.

At login, after password verification, a user with 2FA enabled must submit a valid time-based one-time code before their session is granted full access.

### Session Management
Flask's built-in `session` object stores the logged-in user's ID in a signed cookie. Protected routes check for this before allowing access.

## Security Notes

This project deliberately implements each of the following, rather than treating them as afterthoughts:

| Concern | Mitigation |
|---|---|
| Stolen database exposing passwords | Salted password hashing (never stores plaintext) |
| SQL injection | Parameterized queries via SQLAlchemy ORM |
| Session forgery | Signed session cookies |
| Brute-force login attempts | Rate limiting on the login route |
| Username enumeration | Identical error message for bad username vs. bad password |
| Stolen password alone granting access | Two-factor authentication (TOTP) |
| Incomplete 2FA bypass | Two-step session state |

## Known Limitations / Future Improvements

- No HTTPS in local development
- No account lockout after repeated failed attempts (only rate limiting)
- No password reset flow yet
- No backup/recovery codes for 2FA if a user loses their authenticator device

## WTC User Authentication
WTC-WUHXDE78
