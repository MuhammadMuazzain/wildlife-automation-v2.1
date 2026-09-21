from plotdesk.routes import auth, main, ops, sites


def register_blueprints(app):
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(sites.bp)
    app.register_blueprint(ops.bp)
