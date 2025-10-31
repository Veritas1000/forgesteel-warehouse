from flask import Flask

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    from resources.healthz import healthz
    app.register_blueprint(healthz)

    return app

# @app.route('/')
# def hello_world():
#     return '<p>Hello World</p>'
