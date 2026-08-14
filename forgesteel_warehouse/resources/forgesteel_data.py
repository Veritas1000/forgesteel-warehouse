import logging

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user, jwt_required

from forgesteel_warehouse import db
from forgesteel_warehouse.models import (
    FsHero,
    FsHiddenSettings,
    FsHomebrew,
    FsSession,
)

log = logging.getLogger(__name__)

forgesteel_data = Blueprint("forgesteel_data", __name__)

@forgesteel_data.route("/data")
@jwt_required()
def get_data_types():
    return make_response(jsonify(keys=[
        "forgesteel-heroes",
        "forgesteel-homebrew-settings",
        "forgesteel-session",
        "forgesteel-hidden-setting-ids",
        ]), 200)


@forgesteel_data.get("/data/forgesteel-heroes")
@jwt_required()
def get_heroes():
    data = [hero.data for hero in current_user.heroes] if current_user.heroes is not None else []
    fields = request.args.get("fields")
    if fields is not None:
        fields = fields.split(",")
        filtered = []
        for h in data:
            reduced = {"id": h["id"]}
            for field in fields:
                if field in h:
                    reduced[field] = h[field]

            filtered.append(reduced)
        data = filtered

    return make_response(jsonify(data=data), 200)

@forgesteel_data.get("/data/forgesteel-homebrew-settings")
@jwt_required()
def get_homebrews():
    data = (
        [homebrew.data for homebrew in current_user.homebrew]
        if current_user.homebrew is not None
        else []
    )
    return make_response(jsonify(data=data), 200)

@forgesteel_data.get("/data/<key>")
@jwt_required()
def get_data(key):
    match key:
        case "forgesteel-session":
            data = current_user.session.data if current_user.session is not None else None
        case "forgesteel-hidden-setting-ids":
            data = current_user.hidden_settings.data if current_user.hidden_settings is not None else None
        case _:
            return make_response(jsonify(message=f"Unknown data key: {key}"), 404)

    return make_response(jsonify(data=data), 200)

@forgesteel_data.put("/data/<key>")
@jwt_required()
def put_data(key):
    data = request.get_json()
    match key:
        case "forgesteel-session":
            session = FsSession.query.filter_by(user=current_user).one_or_none()
            if session is None:
                session = FsSession(current_user, data)
                db.session.add(session)
            else:
                session.data = data
        case "forgesteel-hidden-setting-ids":
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
    return make_response(jsonify(), 204)

@forgesteel_data.get("/data/forgesteel-heroes/<hero_id>")
@jwt_required()
def get_hero(hero_id):
    hero = FsHero.query.filter_by(user=current_user, id=hero_id).one_or_404()
    return make_response(jsonify(data=hero.data), 200)


@forgesteel_data.put("/data/forgesteel-heroes/<hero_id>")
@jwt_required()
def save_hero(hero_id):
    hero_data = request.get_json()
    if "id" not in hero_data or hero_data["id"] != hero_id:
        return make_response("Hero id must be present and match the url", 400)

    hero = FsHero.query.filter_by(user=current_user, id=hero_id).one_or_none()

    if hero is None:
        hero = FsHero(current_user, hero_data)
        db.session.add(hero)
    else:
        hero.data = hero_data

    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)


@forgesteel_data.delete("/data/forgesteel-heroes/<hero_id>")
@jwt_required()
def delete_hero(hero_id):
    FsHero.query.filter_by(user=current_user, id=hero_id).one_or_404()
    FsHero.query.filter_by(user=current_user, id=hero_id).delete()
    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)


@forgesteel_data.get("/data/forgesteel-homebrew-settings/<homebrew_id>")
@jwt_required()
def get_homebrew(homebrew_id):
    homebrew = FsHomebrew.query.filter_by(user=current_user, id=homebrew_id).one_or_404()
    return make_response(jsonify(data=homebrew.data), 200)


@forgesteel_data.put("/data/forgesteel-homebrew-settings/<homebrew_id>")
@jwt_required()
def save_homerbrew(homebrew_id):
    request_data = request.get_json()
    if "id" not in request_data or request_data["id"] != homebrew_id:
        return make_response("Homebrew id must be present and match the url", 400)

    homebrew = FsHomebrew.query.filter_by(user=current_user, id=homebrew_id).one_or_none()

    if homebrew is None:
        homebrew = FsHomebrew(current_user, request_data)
        db.session.add(homebrew)
    else:
        homebrew.data = request_data

    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)


@forgesteel_data.delete("/data/forgesteel-homebrew-settings/<homebrew_id>")
@jwt_required()
def delete_homebrew(homebrew_id):
    FsHomebrew.query.filter_by(user=current_user, id=homebrew_id).one_or_404()
    FsHomebrew.query.filter_by(user=current_user, id=homebrew_id).delete()
    db.session.commit()
    db.session.refresh(current_user)
    return make_response(jsonify(), 204)
