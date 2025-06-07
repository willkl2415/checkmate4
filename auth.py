# auth.py
from flask import session, redirect, url_for
import hashlib

users = {
    "analyst": hashlib.sha256("dsat2025".encode()).hexdigest(),
    "admin": hashlib.sha256("admin2025".encode()).hexdigest()
}

user_roles = {
    "analyst": "user",
    "admin": "admin"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    if username in users and users[username] == hash_password(password):
        return True
    return False

def get_role(username):
    return user_roles.get(username, "user")

def login_required(role="user"):
    def wrapper(func):
        def decorated_function(*args, **kwargs):
            if "username" not in session:
                return redirect(url_for("login"))
            if role == "admin" and get_role(session["username"]) != "admin":
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        decorated_function.__name__ = func.__name__
        return decorated_function
    return wrapper
