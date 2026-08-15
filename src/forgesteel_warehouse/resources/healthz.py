import importlib

from flask import Blueprint, jsonify

healthz = Blueprint('healthz', __name__)

@healthz.route('/healthz')
def get_health():
    return jsonify({
        'version': importlib.metadata.version("forgesteel_warehouse"),
        })
