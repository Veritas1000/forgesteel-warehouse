import json
import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .__version__ import __version__

log = logging.getLogger(__name__)

## Initialize global objects
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def init_app(app_config=None):
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    ## Get database URI from environment variables or use default
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI", "sqlite:///:memory:"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    ## Configuration
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "test-jwt-secret-key-change-in-prod"
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-change-in-prod")
    app.config["CRYPT_KEY"] = os.getenv(
        "CRYPT_KEY", "Test_crypt_key_change_in_prod_or_else_12345="
    )

    ## Cookie config
    cookies_secure = os.getenv("COOKIE_SECURE", "True").lower() in ("true", "1", "t")
    cookies_samesite = os.getenv("COOKIE_SAMESITE", "Lax")
    cookies_domain = os.getenv("COOKIE_DOMAIN", None)

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = cookies_secure
    app.config["SESSION_COOKIE_SAMESITE"] = cookies_samesite
    app.config["SESSION_COOKIE_DOMAIN"] = cookies_domain

    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]

    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_CSRF_METHODS"] = ["POST", "PUT", "PATCH", "DELETE"]
    app.config["JWT_COOKIE_SECURE"] = cookies_secure
    app.config["JWT_COOKIE_SAMESITE"] = cookies_samesite
    app.config["JWT_COOKIE_DOMAIN"] = cookies_domain

    app.config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "ERROR")

    ## If no passed in config, but a config path is set, load config
    config_path = os.getenv("FSW_CONFIG_PATH")
    if app_config is None and config_path is not None:
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                app_config = json.load(config_file)
        except:
            app_config = None

    ## Prioritize passed in config over all
    if app_config:
        app.config.update(app_config)

    ## Logging setup
    level = logging.NOTSET
    match app.config["LOG_LEVEL"]:
        case "TRACE":
            level = 5 ## debug is 10, we define a level deeper than that
        case "DEBUG":
            level = logging.DEBUG
        case "INFO":
            level = logging.INFO
        case "WARNING":
            level = logging.WARNING
        case "ERROR" | _:
            level = logging.ERROR

    root = logging.getLogger("forgesteel_warehouse")
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    ## Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)

    with app.app_context():

        from .resources.healthz import healthz

        app.register_blueprint(healthz)

        from .resources.token_handler import token_handler

        app.register_blueprint(token_handler)

        from .resources.forgesteel_connector import forgesteel_connector

        app.register_blueprint(forgesteel_connector)

        from .resources.forgesteel_data import forgesteel_data

        app.register_blueprint(forgesteel_data)

        return app
