import logging

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user, jwt_required

from forgesteel_warehouse import db
from forgesteel_warehouse.models import (
    FsHeroes,
    FsHiddenSettings,
    FsHomebrew,
    FsSession,
)

log = logging.getLogger(__name__)

forgesteel_data = Blueprint('forgesteel_data', __name__)

@forgesteel_data.route('/data')
@jwt_required()
def get_data_types():
    return make_response(jsonify(keys=[
        'forgesteel-heroes',
        'forgesteel-homebrew-settings',
        'forgesteel-session',
        'forgesteel-hidden-setting-ids',
        ]), 200)

@forgesteel_data.get('/data/<key>')
@jwt_required()
def get_data(key):
    match key:
        case "forgesteel-heroes":
            data = current_user.heroes.data if current_user.heroes is not None else None
        case 'forgesteel-homebrew-settings':
            data = current_user.homebrew.data if current_user.homebrew is not None else None
        case 'forgesteel-session':
            data = current_user.session.data if current_user.session is not None else None
        case 'forgesteel-hidden-setting-ids':
            data = current_user.hidden_settings.data if current_user.hidden_settings is not None else None
        case _:
            return make_response(jsonify(message=f"Unknown data key: {key}"), 404)

    return make_response(jsonify(data=data), 200)

@forgesteel_data.put('/data/<key>')
@jwt_required()
def put_data(key):
    data = request.get_json()
    resp = make_response(jsonify(), 204)
    match key:
        case "forgesteel-heroes":
            resp.headers["Deprecation"] = "@1777247999"
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
        case 'forgesteel-session':
            session = FsSession.query.filter_by(user=current_user).one_or_none()
            if session is None:
                session = FsSession(current_user, data)
                db.session.add(session)
            else:
                session.data = data
        case 'forgesteel-hidden-setting-ids':
            hidden_settings = FsHiddenSettings.query.filter_by(user=current_user).one_or_none()
            if hidden_settings is None:
                hidden_settings = FsHiddenSettings(current_user, data)
                db.session.add(hidden_settings)
            else:
                hidden_settings.data = data
        case _:
            return make_response(jsonify(message=f"Unknown data key: {key}"), 404)

    db.session.commit()
    db.session.refresh(current_user)
    return resp


@forgesteel_data.get('/data/forgesteel-heroes/<hero_id>')
@jwt_required()
def get_hero(hero_id):
    heroes_data = FsHeroes.query.filter_by(user=current_user).one_or_404()
    all_heroes = heroes_data.data

    matching_heroes = [hero for hero in all_heroes if hero["id"] == hero_id]
    count = len(matching_heroes)
    status = 200
    if count == 0:
        return make_response(jsonify(msg='No hero with that ID found'), 404)
    elif count > 1:
        status = 206

    hero = matching_heroes[0]
    return make_response(jsonify(data=hero), status)


@forgesteel_data.put("/data/forgesteel-heroes/<hero_id>")
@jwt_required()
def save_hero(hero_id):
    hero_data = request.get_json()

    ## Verify that hero id in data matches id in url
    if "id" not in hero_data or hero_id != hero_data["id"]:
        return make_response(jsonify(msg="Hero id data must match url"), 400)

    heroes_data = FsHeroes.query.filter_by(user=current_user).one_or_none()
    all_heroes = heroes_data.data if heroes_data is not None else []

    ## loop through heroes and remove mathing id
    all_heroes = [hero for hero in all_heroes if hero["id"] != hero_id]
    all_heroes.append(hero_data)

    if heroes_data is None:
        heroes = FsHeroes(current_user, all_heroes)
        db.session.add(heroes)
    else:
        current_user.heroes.data = all_heroes

    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)


@forgesteel_data.delete("/data/forgesteel-heroes/<hero_id>")
@jwt_required()
def delete_hero(hero_id):
    all_heroes_obj = FsHeroes.query.filter_by(user=current_user).one_or_404()
    all_heroes = all_heroes_obj.data if all_heroes_obj is not None else []

    if not any(hero["id"] == hero_id for hero in all_heroes):
        return make_response(jsonify(), 404)

    ## loop through heroes and remove mathing id
    updated_heroes = [hero for hero in all_heroes if hero["id"] != hero_id]
    current_user.heroes.data = updated_heroes

    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)

