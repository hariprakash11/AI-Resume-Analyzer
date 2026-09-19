"""Application factory and shared Flask extensions."""

import os

from flask import (
    Flask,
    render_template,
)

from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    """Create and configure the AI Resume Analyzer application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    database_uri = app.config.get(
        "SQLALCHEMY_DATABASE_URI",
        ""
    )

    if database_uri.startswith("sqlite:///"):

        database_path = database_uri.removeprefix(
            "sqlite:///"
        )

        database_directory = os.path.dirname(
            database_path
        )

        if database_directory:
            os.makedirs(
                database_directory,
                exist_ok=True
            )

    db.init_app(app)


    # =====================================================
    # MODELS
    # =====================================================

    # Import models before db.create_all() so SQLAlchemy
    # knows about all database tables.

    from app.models.user import User
    from app.models.resume import Resume


    # =====================================================
    # ROUTES
    # =====================================================

    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.home import home
    from app.routes.resume import resume
    from app.routes.report import report


    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(resume)
    app.register_blueprint(report)


    # =====================================================
    # ERROR HANDLERS
    # =====================================================

    @app.errorhandler(404)
    def page_not_found(error):
        """Handle requests for routes that do not exist."""

        return render_template(
            "errors/404.html"
        ), 404


    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle unexpected application errors."""

        db.session.rollback()

        app.logger.exception(
            "Unhandled application error."
        )

        return render_template(
            "errors/500.html"
        ), 500


    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    with app.app_context():

        db.create_all()


    return app