from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from plotdesk.extensions import mongo
from plotdesk.helpers import login_required

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("auth.register"))

        role = request.form.get("role") or "applicant"
        if role not in ("applicant", "coordinator"):
            role = "applicant"

        mongo.db.users.insert_one(
            {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password")),
                "full-name": request.form.get("full-name").title(),
                "phone": request.form.get("phone"),
                "role": role,
            }
        )
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("auth.profile", username=session["user"]))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user" not in session:
        if request.method == "POST":
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()}
            )
            if existing_user:
                if check_password_hash(
                    existing_user["password"], request.form.get("password")
                ):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(session["user"]))
                    return redirect(
                        url_for("auth.profile", username=session["user"])
                    )
                flash("Incorrect Password, Please try again")
                return redirect(url_for("auth.login"))
            flash("Incorrect Username, Please try again")
            return redirect(url_for("auth.login"))
        return render_template("auth/login.html")
    return redirect(url_for("auth.profile", username=session["user"]))


@bp.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    if request.method == "POST":
        mongo.db.users.update_one(
            {"username": session["user"]},
            {
                "$set": {
                    "full-name": request.form.get("name"),
                    "phone": request.form.get("phone"),
                }
            },
        )
        flash("Contact Details Successfully Updated")

    user = mongo.db.users.find_one({"username": session["user"]})
    return render_template(
        "auth/profile.html",
        username=user["username"],
        fullname=user.get("full-name", ""),
        phone=user.get("phone", ""),
        role=user.get("role", "applicant"),
    )


@bp.route("/logout")
@login_required
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("auth.login"))
