from flask import Blueprint, jsonify
from forgesteel_vault import __version__

healthz = Blueprint('healthz', __name__)

@healthz.route('/healthz')
def get_health():
    return jsonify({
        'version': __version__,
        })
