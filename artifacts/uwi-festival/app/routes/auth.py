from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db
from ..models import User
from .utils import safe_next_url

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=request.form.get("remember") == "on")
            next_page = safe_next_url(request.args.get("next"))
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(next_page or _role_dashboard(user.role))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        affiliation = request.form.get("affiliation", "").strip()
        discipline = request.form.get("discipline", "").strip()
        role = request.form.get("role", "attendee")

        if role not in ("author", "attendee"):
            role = "attendee"

        if not email or not password or not first_name or not last_name:
            flash("Email, password, first name, and last name are required.", "danger")
            return render_template("auth/signup.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("auth/signup.html")

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            affiliation=affiliation,
            discipline=discipline,
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Account created successfully! Welcome, {user.first_name}.", "success")
        return redirect(_role_dashboard(user.role))
    return render_template("auth/signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name", current_user.first_name).strip()
        current_user.last_name = request.form.get("last_name", current_user.last_name).strip()
        current_user.affiliation = request.form.get("affiliation", "").strip()
        current_user.discipline = request.form.get("discipline", "").strip()
        current_user.bio = request.form.get("bio", "").strip()
        new_password = request.form.get("new_password", "")
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Profile updated successfully.", "success")
    return render_template("auth/profile.html")


def _role_dashboard(role):
    dashboards = {
        "admin": "admin.dashboard",
        "author": "author.dashboard",
        "reviewer": "reviewer.dashboard",
        "attendee": "attendee.dashboard",
        "judge": "judge.dashboard",
        "usher": "usher.dashboard",
    }
    return url_for(dashboards.get(role, "public.index"))
