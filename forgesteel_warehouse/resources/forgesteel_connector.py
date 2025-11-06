import logging

from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token, jwt_required, current_user

from forgesteel_warehouse.models import User

log = logging.getLogger(__name__)

forgesteel_connector = Blueprint('forgesteel_connector', __name__)

@forgesteel_connector.route('/connect')
def connect():
    auth = request.authorization
    if auth and auth.token:
        try:
            user = User.find_by_api_token(auth.token)
            if user:
                access_token = create_access_token(identity=user)
                return jsonify(access_token=access_token) 
        except:
            pass
        return make_response(jsonify(message='Invalid token'), 401, {'WWW-Authenticate': 'Bearer realm="Authorization required"'})

    return make_response(jsonify(message='Token required'), 400, {'WWW-Authenticate': 'Bearer realm="Authorization required"'})

@forgesteel_connector.route('/me')
@jwt_required()
def me():
    return make_response(jsonify(logged_in_as=current_user.name), 200)
