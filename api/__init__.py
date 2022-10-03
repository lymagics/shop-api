import os

from apiflask import APIFlask
from flask import redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from config import base_dir, Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
mail = Mail()


def create_app(config=Config) -> APIFlask:
    """Application factory function."""
    app = APIFlask(
        __name__,
        title="Shop API",
        version="1.0.0",
        docs_ui="elements"
    )
    app.config.from_object(config)
    app.config["DESCRIPTION"] = read_description()
    app.config["DOCS_FAVICON"] = "static/favicon.ico"

    from api import models

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    if app.config["USE_CORS"]:
        cors.init_app(app)
    mail.init_app(app)

    # Blueprints
    register_blueprints(app)

    @app.get("/")
    @app.doc(hide=True)
    def index():
        """Always redirect from index to docs page."""
        return redirect(url_for("openapi.docs"))

    return app 


def register_blueprints(app: APIFlask) -> None:
    """Register application blueprints."""
    from .categories import categories
    app.register_blueprint(categories, url_prefix="/api")

    from .carts import carts
    app.register_blueprint(carts, url_prefix="/api")

    from .populate import populate
    app.register_blueprint(populate)

    from .products import products
    app.register_blueprint(products, url_prefix="/api")

    from .users import users 
    app.register_blueprint(users, url_prefix="/api")

    from .tokens import tokens 
    app.register_blueprint(tokens, url_prefix="/api")


def read_description(filename: str="api/templates/docs/description.md") -> str:
    """Read OpenAPI description."""
    with open(os.path.join(base_dir, filename)) as description:
        return description.read()
