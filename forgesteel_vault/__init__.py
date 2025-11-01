from flask import Flask
from .__version__ import __version__

def init_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        from resources.healthz import healthz
        app.register_blueprint(healthz)

        return app
