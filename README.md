# PlotDesk

Flask + MongoDB web app for registering **community garden plots** — shared grow sites where members apply for beds, coordinators review capacity, and the network keeps a single map of active plots.

This repository is a **capped-down public version** of a system built for a real client engagement. Client identity and proprietary details are confidential and are not included here. The production build covers additional workflows, data rules, and integrations; what you see in this repo is a focused slice of that work: applications, plot records, coordinator assignment, spreadsheet import, and a shared map.

Garden networks often collect plot applications through a hosted form (email summary), type those rows into a shared spreadsheet, then manually refresh a separate map. PlotDesk replaces that loop with one small web app: apply online, store plots in a database, assign coordinators, import existing spreadsheet data, and show geocoded plots on a map.

---

## Author & credits

| Role | Who |
| --- | --- |
| **Author / maintainer** | Muhammad Muazzain |

---

## Scope of this repo vs the client build

| In this public version | Held back (client / confidential) |
| --- | --- |
| Garden plot application webform | Full client branding, org rules, and private data model |
| Plot list, search, status workflow | Extended CRM-style modules from the full build |
| Coordinator assignment on plots | Client-specific roles, notifications, and integrations |
| CSV import of master plot data | Direct spreadsheet formats and private master files |
| Shared map of geocoded plots | Client map accounts and operational dashboards |

---

## Implementation overview

| Area | Implementation |
| --- | --- |
| App entry | `run.py` + `plotdesk/` package — blueprints for auth, sites, map/import |
| Templates | Jinja under `templates/` (`layouts/`, `main/`, `auth/`, `sites/`, `ops/`) |
| Static assets | `static/css`, `static/js`, `static/images`, `static/sample_data` |
| Database | MongoDB collections: `garden_plots`, `users`, `notes`, `site_numbers`, plus optional `crop_focuses` / `facilities` / `status` |
| Auth | Session login; password hashing via Werkzeug; roles `applicant` \| `coordinator` \| `admin` |
| Pagination / search | `flask-paginate`; text index when present, regex fallback otherwise |
| Map | Leaflet + OpenStreetMap tiles; markers from `latitude` / `longitude` on plot docs |
| Address assist (optional) | Google Places when `GOOGLE_MAPS_API_KEY` is set |
| Photos (optional) | Cloudinary upload widget (configure cloud name + preset in the browser) |
| Spreadsheet import | CSV upload on `/import` (coordinators); sample file in `static/sample_data/sites_import_sample.csv` |

### Routes

| Path | Purpose |
| --- | --- |
| `/` | Product overview |
| `/register`, `/login`, `/logout` | Auth (register as applicant or plot coordinator) |
| `/profile/<username>` | Contact details |
| `/sites` | Plot list with filters (my applications, pending, active, assigned to me) |
| `/search` | Search plots |
| `/sites/apply` | Garden plot **webform** application |
| `/sites/<id>` | View / edit plot, status, notes; coordinators can assign a coordinator |
| `/sites/<id>/delete` | Delete plot + linked notes |
| `/map` | Shared map of geocoded plots |
| `/import` | Load master CSV into `garden_plots` (coordinator/admin) |

### Status workflow

`Pending Review` → `Approved` → `Active` (also `On Hold`, `Closed`)

### `garden_plots` fields (high level)

- Identity: `site_number`, `property_name`, `status`, `created_by`
- Contact: `contact_name`, `phone`, `email`
- Location: `address`, `suburb`, `postcode`, `state`, `location`, `latitude`, `longitude`
- Capacity: `crop_focus`, `capacity`, `facilities`, `available_from`
- Ops: `assigned_coordinator`, `notes[]`, optional `image_url`, `imported_from`

---

## What this version delivers

- First-party webform + database instead of form-email → spreadsheet retyping
- A small coordinator group can filter, assign, and update plots in one place
- Import of existing master plot data via CSV
- Shared map of geocoded plots without a separate manual map feed

---

## Stack

- Python, Flask, Jinja2
- MongoDB (`Flask-PyMongo`)
- Bootstrap 5 + Bootstrap Icons
- Leaflet / OpenStreetMap
- Optional: Google Places, Cloudinary

---

## Local setup

1. Clone this repository and create a virtualenv.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `env.py` (gitignored locally) or set environment variables:

```python
import os
os.environ["MONGO_URI"] = "mongodb+srv://..."
os.environ["MONGO_DBNAME"] = "plot_desk"
os.environ["SECRET_KEY"] = "change-me"
os.environ.setdefault("IP", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
# optional:
# os.environ["GOOGLE_MAPS_API_KEY"] = "..."
```

4. Run the app:

```bash
python run.py
```

5. Register an account as **Plot coordinator** to use Import.
6. Try `static/sample_data/sites_import_sample.csv` on `/import`, then open `/map`.

Admin username recognised in code: `admin@plotdesk.app`.

### Suggested MongoDB text index

```js
db.garden_plots.createIndex({
  site_number: "text",
  property_name: "text",
  suburb: "text",
  address: "text",
  crop_focus: "text",
  created_by: "text",
  assigned_coordinator: "text"
})
```

---

## Project layout (key paths)

```
run.py                      # app entrypoint
plotdesk/                   # Flask application package
  __init__.py               # create_app()
  constants.py              # admin usernames, defaults
  extensions.py             # Mongo
  helpers.py                # auth helpers, plot numbering
  routes/                   # blueprints: main, auth, sites, ops
templates/                  # layouts/, main/, auth/, sites/, ops/
static/js/                  # site-edit, media-upload, address-autocomplete
static/sample_data/         # sites_import_sample.csv
```

---

## Credits

- **Author / maintainer:** Muhammad Muazzain
- Map tiles © OpenStreetMap contributors
