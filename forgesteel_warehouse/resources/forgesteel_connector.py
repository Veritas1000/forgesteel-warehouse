import logging

from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, current_user, set_access_cookies, set_refresh_cookies

from forgesteel_warehouse.models import User

log = logging.getLogger(__name__)

forgesteel_connector = Blueprint('forgesteel_connector', __name__)

@forgesteel_connector.post('/connect')
def connect():
    auth = request.authorization
    if auth is None:
        log.debug('No authorization header!')

    if auth and auth.token:
        try:
            user = User.find_by_api_token(auth.token)
            if user:
                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)
                resp = make_response(jsonify(access_token=access_token, refresh_token=refresh_token), 200)
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
        
                return resp
        except:
            pass
        return make_response(jsonify(message='Invalid token'), 401, {'WWW-Authenticate': 'Bearer realm="Authorization required"'})

    return make_response(jsonify(message='Token required'), 400, {'WWW-Authenticate': 'Bearer realm="Authorization required"'})

@forgesteel_connector.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)

@forgesteel_connector.route('/me')
@jwt_required()
def me():
    return make_response(jsonify(logged_in_as=current_user.name), 200)
