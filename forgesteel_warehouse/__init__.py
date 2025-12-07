import json
import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///:memory:')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ## Configuration
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key-change-in-prod'
    app.config['SECRET_KEY'] ='test-secret-key-change-in-prod'
    
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_CSRF_METHODS'] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    ## TODO: Enable these once possible
    # app.config['JWT_COOKIE_SAMESITE'] = 'None'
    # app.config['JWT_COOKIE_SECURE'] = True

    app.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'ERROR')

    ## If no passed in config, but a config path is set, load config
    config_path = os.getenv('FSW_CONFIG_PATH')
    if app_config is None and config_path is not None:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            try:
                app_config = json.load(config_file)
            except:
                app_config = None

    ## Prioritize passed in config over all
    if app_config:
        app.config.update(app_config)

    ## Logging setup
    level = logging.NOTSET
    match app.config['LOG_LEVEL']:
        case 'DEBUG':
            level = logging.DEBUG
        case 'INFO':
            level = logging.INFO
        case 'WARNING':
            level = logging.WARNING
        case 'Error' | _:
            level = logging.ERROR

    root = logging.getLogger('forgesteel_warehouse')
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
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
