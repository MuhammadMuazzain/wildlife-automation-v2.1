import os
from pathlib import Path

from flask import Flask, render_template

from plotdesk.constants import load_env_file
from plotdesk.extensions import mongo
from plotdesk.routes import register_blueprints

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    load_env_file()

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.secret_key = os.environ.get("SECRET_KEY")
    app.config["GOOGLE_MAPS_API_KEY"] = os.environ.get("GOOGLE_MAPS_API_KEY", "")

    mongo.init_app(app)
    register_blueprints(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("main/not_found.html"), 404

    return app
