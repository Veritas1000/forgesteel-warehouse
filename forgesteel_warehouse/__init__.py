import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from .__version__ import __version__

log = logging.getLogger(__name__)

## Initialize global objects
db = SQLAlchemy()
jwt = JWTManager()

def init_app(app_config=None):
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    ## Logging setup
    root = logging.getLogger('forgesteel_warehouse')
    # root.setLevel(logging.WARNING)
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.WARNING)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    ## Get database URI from environment variables or use default
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///:memory:')

    if app_config:
        app.config.update(app_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ## Configuration
    app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    
    ## Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():

        from .resources.healthz import healthz
        app.register_blueprint(healthz)
        
        from .resources.patreon_oauth import patreon_oauth
        app.register_blueprint(patreon_oauth)

        from .resources.forgesteel_connector import forgesteel_connector
        app.register_blueprint(forgesteel_connector)

        return app

## pretty sure this needs to go elsewhere
# if __name__ == "__main__":
#     app = init_app()
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
