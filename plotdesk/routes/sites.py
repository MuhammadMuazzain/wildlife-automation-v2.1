import datetime

from bson.objectid import ObjectId
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_paginate import Pagination, get_page_args

from plotdesk.constants import (
    ADMIN_USERNAMES,
    DEFAULT_CROP_FOCUSES,
    DEFAULT_FACILITIES,
    DEFAULT_STATUSES,
)
from plotdesk.extensions import mongo
from plotdesk.helpers import is_coordinator_or_admin, login_required, next_site_number

bp = Blueprint("sites", __name__)


@bp.route("/sites")
@login_required
def list_sites():
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    filter_name = request.args.get("filter")

    if filter_name == "pending":
        query = {"status": "Pending Review"}
    elif filter_name == "user":
        query = {"created_by": session["user"]}
    elif filter_name == "active":
        query = {"status": "Active"}
    elif filter_name == "assigned":
        query = {"assigned_coordinator": session["user"]}
    else:
        query = {}

    sites = list(mongo.db.garden_plots.find(query).sort("site_number", -1))
    total = len(sites)
    paginated = sites[offset: offset + per_page]
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework="bootstrap4",
        record_name="plots",
    )
    return render_template(
        "sites/list.html",
        sites=paginated,
        page=page,
        per_page=per_page,
        pagination=pagination,
        is_coordinator=is_coordinator_or_admin(),
    )


@bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    query_text = request.form.get("query") or request.args.get("query") or ""
    try:
        sites = list(
            mongo.db.garden_plots.find({"$text": {"$search": query_text}})
        )
    except Exception:
        regex = {"$regex": query_text, "$options": "i"}
        sites = list(
            mongo.db.garden_plots.find(
                {
                    "$or": [
                        {"site_number": regex},
                        {"property_name": regex},
                        {"suburb": regex},
                        {"address": regex},
                        {"crop_focus": regex},
                        {"created_by": regex},
                        {"assigned_coordinator": regex},
                    ]
                }
            )
        )

    total = len(sites)
    paginated = sites[offset: offset + per_page]
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework="bootstrap4",
        record_name="plots",
    )
    return render_template(
        "sites/list.html",
        sites=paginated,
        page=page,
        per_page=per_page,
        pagination=pagination,
        is_coordinator=is_coordinator_or_admin(),
    )


@bp.route("/sites/apply", methods=["GET", "POST"])
@login_required
def apply():
    if request.method == "POST":
        site_no = next_site_number()
        site = {
            "application_date": request.form.get("application_date"),
            "property_name": request.form.get("property_name"),
            "contact_name": request.form.get("contact_name"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),
            "suburb": request.form.get("suburb"),
            "postcode": request.form.get("postcode"),
            "state": request.form.get("state") or "",
            "location": request.form.get("location"),
            "latitude": request.form.get("latitude") or "",
            "longitude": request.form.get("longitude") or "",
            "crop_focus": request.form.get("crop_focus"),
            "capacity": request.form.get("capacity"),
            "facilities": request.form.get("facilities"),
            "available_from": request.form.get("available_from"),
            "image_url": request.form.get("image_url"),
            "notes": [],
            "status": "Pending Review",
            "assigned_coordinator": "",
            "site_number": site_no,
            "created_by": session["user"],
        }
        result = mongo.db.garden_plots.insert_one(site)
        site_id = result.inserted_id

        if request.form.get("notes"):
            note = {
                "site_id": ObjectId(site_id),
                "date_time": datetime.datetime.now().strftime("%d %b %Y  %X"),
                "note": request.form.get("notes"),
            }
            note_id = mongo.db.notes.insert_one(note)
            mongo.db.garden_plots.update_one(
                {"_id": ObjectId(site_id)},
                {"$push": {"notes": ObjectId(note_id.inserted_id)}},
            )

        flash(f"Garden plot application saved as plot #{site_no}")
        return redirect(url_for("sites.list_sites"))

    crop_focuses = list(mongo.db.crop_focuses.find().sort("name", 1)) or list(
        DEFAULT_CROP_FOCUSES
    )
    facilities = list(mongo.db.facilities.find().sort("name", 1)) or list(
        DEFAULT_FACILITIES
    )
    return render_template(
        "sites/apply.html",
        crop_focuses=crop_focuses,
        facilities=facilities,
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
    )


@bp.route("/sites/<site_id>", methods=["GET", "POST"])
@login_required
def detail(site_id):
    site = mongo.db.garden_plots.find_one({"_id": ObjectId(site_id)})
    if not site:
        flash("Garden plot not found")
        return redirect(url_for("sites.list_sites"))

    can_edit = (
        session["user"].lower() == site.get("created_by", "").lower()
        or session["user"].lower() in ADMIN_USERNAMES
        or is_coordinator_or_admin()
    )

    if request.method == "POST":
        if not can_edit:
            flash("You do not have permission to update this plot")
            return redirect(url_for("sites.detail", site_id=site_id))

        submit = {
            "application_date": request.form.get("application_date"),
            "property_name": request.form.get("property_name"),
            "contact_name": request.form.get("contact_name"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),
            "suburb": request.form.get("suburb"),
            "postcode": request.form.get("postcode"),
            "state": request.form.get("state"),
            "location": request.form.get("location"),
            "latitude": request.form.get("latitude") or "",
            "longitude": request.form.get("longitude") or "",
            "crop_focus": request.form.get("crop_focus"),
            "capacity": request.form.get("capacity"),
            "facilities": request.form.get("facilities"),
            "available_from": request.form.get("available_from"),
            "image_url": request.form.get("image_url"),
            "status": request.form.get("status"),
        }

        if is_coordinator_or_admin():
            submit["assigned_coordinator"] = (
                request.form.get("assigned_coordinator") or ""
            )

        if request.form.get("notes"):
            note = {
                "site_id": ObjectId(site_id),
                "date_time": datetime.datetime.now().strftime("%d %b %Y  %X"),
                "note": request.form.get("notes"),
            }
            note_id = mongo.db.notes.insert_one(note)
            mongo.db.garden_plots.update_one(
                {"_id": ObjectId(site_id)},
                {"$push": {"notes": ObjectId(note_id.inserted_id)}},
            )

        mongo.db.garden_plots.update_one(
            {"_id": ObjectId(site_id)}, {"$set": submit}
        )
        flash("Garden plot successfully updated")
        return redirect(url_for("sites.detail", site_id=site_id))

    notes_array = mongo.db.notes.find({"site_id": ObjectId(site_id)}).sort(
        "date_time", -1
    )
    statuses = list(mongo.db.status.find().sort("status", 1)) or list(DEFAULT_STATUSES)
    coordinators = list(
        mongo.db.users.find(
            {"role": {"$in": ["coordinator", "admin"]}},
            {"username": 1, "full-name": 1},
        )
    )
    return render_template(
        "sites/detail.html",
        site=site,
        notes_array=notes_array,
        statuses=statuses,
        coordinators=coordinators,
        can_edit=can_edit,
        is_coordinator=is_coordinator_or_admin(),
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
    )


@bp.route("/sites/<site_id>/delete")
@login_required
def delete(site_id):
    site = mongo.db.garden_plots.find_one({"_id": ObjectId(site_id)})
    if not site:
        flash("Garden plot not found")
        return redirect(url_for("sites.list_sites"))

    allowed = (
        session["user"].lower() == site.get("created_by", "").lower()
        or session["user"].lower() in ADMIN_USERNAMES
        or is_coordinator_or_admin()
    )
    if not allowed:
        flash("You do not have permission to delete this plot")
        return redirect(url_for("sites.list_sites"))

    mongo.db.garden_plots.delete_one({"_id": ObjectId(site_id)})
    mongo.db.notes.delete_many({"site_id": ObjectId(site_id)})
    flash("Garden plot successfully deleted")
    return redirect(url_for("sites.list_sites"))
