import logging

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, current_user

from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHeroes, FsHomebrew

log = logging.getLogger(__name__)

forgesteel_data = Blueprint('forgesteel_data', __name__)

@forgesteel_data.route('/data')
@jwt_required()
def get_data_types():
    return make_response(jsonify(keys=[
        'forgesteel-heroes',
        'forgesteel-homebrew-settings'
        ]), 200)

@forgesteel_data.get('/data/<key>')
@jwt_required()
def get_data(key):
    match key:
        case 'forgesteel-heroes':
            data = current_user.heroes.data if current_user.heroes is not None else None
            return make_response(jsonify(data=data), 200)
        case 'forgesteel-homebrew-settings':
            data = current_user.homebrew.data if current_user.homebrew is not None else None
            return make_response(jsonify(data=data), 200)
        case _:
            return make_response(jsonify(message=f"Unknown data key: {key}"), 404)

@forgesteel_data.put('/data/<key>')
@jwt_required()
def put_data(key):
    data = request.get_json()
    match key:
        case 'forgesteel-heroes':
            heroes = FsHeroes.query.filter_by(user=current_user).one_or_none()
            if heroes is None:
                heroes = FsHeroes(current_user, data)
                db.session.add(heroes)
            else:
                heroes.data = data
        case 'forgesteel-homebrew-settings':
            homebrew = FsHomebrew.query.filter_by(user=current_user).one_or_none()
            if homebrew is None:
                homebrew = FsHomebrew(current_user, data)
                db.session.add(homebrew)
            else:
                homebrew.data = data
        case _:
            return make_response(jsonify(message=f"Unknown data key: {key}"), 404)
    
    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)
