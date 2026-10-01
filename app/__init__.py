import os
from flask import Flask, render_template
from config import config_by_name
from app.models import db

def create_app(config_name=None):
    """
    Application factory for TaskFlow.
    Initializes configuration, extensions, blueprints, and error handlers.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)

    # Register Jinja2 template filters
    @app.template_filter("format_date")
    def format_date(value, format_str="%b %d, %Y"):
        """Formats string or date object into a human-friendly string."""
        if not value:
            return "No date"
        if isinstance(value, str):
            try:
                from datetime import datetime
                dt = datetime.strptime(value.split()[0], "%Y-%m-%d")
                return dt.strftime(format_str)
            except ValueError:
                return value
        return value.strftime(format_str)

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        """Custom 404 error handler with user-friendly design."""
        return render_template("404.html", error_message="The page or task you are looking for does not exist."), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Custom 500 error handler avoiding trace leakage."""
        return render_template("500.html", error_message="Something went wrong on our end. Please try again shortly."), 500

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Context processor to inject common variables into all templates
    @app.context_processor
    def inject_global_vars():
        from datetime import date
        return {
            "current_year": date.today().year,
            "today_date": date.today().strftime("%A, %B %d, %Y")
        }

    return app
