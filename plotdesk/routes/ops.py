import csv
import datetime
import io

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from plotdesk.extensions import mongo
from plotdesk.helpers import is_coordinator_or_admin, login_required, next_site_number

bp = Blueprint("ops", __name__)


@bp.route("/map")
@login_required
def sites_map():
    sites = list(
        mongo.db.garden_plots.find(
            {
                "latitude": {"$nin": ["", None]},
                "longitude": {"$nin": ["", None]},
            }
        )
    )
    map_points = []
    for site in sites:
        try:
            lat = float(site.get("latitude"))
            lng = float(site.get("longitude"))
        except (TypeError, ValueError):
            continue
        map_points.append(
            {
                "site_number": site.get("site_number"),
                "property_name": site.get("property_name"),
                "suburb": site.get("suburb"),
                "status": site.get("status"),
                "crop_focus": site.get("crop_focus"),
                "assigned_coordinator": site.get("assigned_coordinator")
                or "Unassigned",
                "lat": lat,
                "lng": lng,
                "id": str(site["_id"]),
            }
        )
    return render_template("ops/map.html", map_points=map_points)


@bp.route("/import", methods=["GET", "POST"])
@login_required
def import_sites():
    if not is_coordinator_or_admin():
        flash("Only plot coordinators can import master data")
        return redirect(url_for("sites.list_sites"))

    summary = None
    if request.method == "POST":
        upload = request.files.get("spreadsheet")
        if not upload or not upload.filename:
            flash("Please choose a CSV file to upload")
            return redirect(url_for("ops.import_sites"))

        if not upload.filename.lower().endswith(".csv"):
            flash("Import accepts CSV only (export Excel as CSV)")
            return redirect(url_for("ops.import_sites"))

        raw = upload.read().decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(raw))
        created = 0
        skipped = 0
        for row in reader:
            property_name = (
                row.get("property_name") or row.get("Property Name") or ""
            ).strip()
            address = (row.get("address") or row.get("Address") or "").strip()
            if not property_name and not address:
                skipped += 1
                continue

            site_no = next_site_number()
            site = {
                "application_date": (
                    row.get("application_date")
                    or row.get("Application Date")
                    or datetime.date.today().isoformat()
                ),
                "property_name": property_name,
                "contact_name": row.get("contact_name")
                or row.get("Contact Name")
                or "",
                "phone": row.get("phone") or row.get("Phone") or "",
                "email": row.get("email") or row.get("Email") or "",
                "address": address,
                "suburb": row.get("suburb") or row.get("Suburb") or "",
                "postcode": row.get("postcode") or row.get("Postcode") or "",
                "state": row.get("state") or row.get("State") or "",
                "location": row.get("location") or address,
                "latitude": row.get("latitude") or row.get("Latitude") or "",
                "longitude": row.get("longitude") or row.get("Longitude") or "",
                "crop_focus": row.get("crop_focus")
                or row.get("Crop Focus")
                or "",
                "capacity": row.get("capacity") or row.get("Capacity") or "",
                "facilities": row.get("facilities") or row.get("Facilities") or "",
                "available_from": row.get("available_from")
                or row.get("Available From")
                or "",
                "image_url": "",
                "notes": [],
                "status": row.get("status") or row.get("Status") or "Active",
                "assigned_coordinator": row.get("assigned_coordinator")
                or row.get("Assigned Coordinator")
                or "",
                "site_number": site_no,
                "created_by": session["user"],
                "imported_from": upload.filename,
            }
            mongo.db.garden_plots.insert_one(site)
            created += 1

        summary = {"created": created, "skipped": skipped}
        flash(f"Import complete: {created} plots loaded, {skipped} rows skipped")

    return render_template("ops/import.html", summary=summary)
