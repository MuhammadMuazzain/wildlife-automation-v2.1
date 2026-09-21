from functools import wraps

from flask import flash, redirect, session, url_for

from plotdesk.constants import ADMIN_USERNAMES
from plotdesk.extensions import mongo


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            flash("You must log in to view this page")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def current_user_doc():
    if "user" not in session:
        return None
    return mongo.db.users.find_one({"username": session["user"]})


def is_coordinator_or_admin():
    user = current_user_doc()
    if not user:
        return False
    if session["user"] in ADMIN_USERNAMES:
        return True
    return user.get("role", "applicant") in ("coordinator", "admin")


def next_site_number():
    from plotdesk.constants import SITE_COUNTER_KEY

    counter = mongo.db.site_numbers.find_one_and_update(
        {"_id": SITE_COUNTER_KEY},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True,
    )
    if not counter or "sequence_value" not in counter:
        mongo.db.site_numbers.update_one(
            {"_id": SITE_COUNTER_KEY},
            {"$setOnInsert": {"sequence_value": 1000}},
            upsert=True,
        )
        counter = mongo.db.site_numbers.find_one_and_update(
            {"_id": SITE_COUNTER_KEY},
            {"$inc": {"sequence_value": 1}},
            return_document=True,
        )
    return str(counter["sequence_value"])
