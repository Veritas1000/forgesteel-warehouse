import logging
import os
import uuid

from flask import Blueprint, Response, current_app, jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
)
from requests import HTTPError

from forgesteel_warehouse import db
from forgesteel_warehouse.models import User
from forgesteel_warehouse.utils.patreon_api import PatreonApi
from forgesteel_warehouse.utils.patreon_logic import has_warehouse_access

token_handler = Blueprint('token_handler', __name__)

log = logging.getLogger(__name__)

TEMP_LOGIN_COOKIE_NAME = 'fs-th-login-temp'


## Gets the current session, if present
@token_handler.get("/th/session")
@jwt_required(optional=True)
def get_session():
    if current_user:
        token = current_user.get_patreon_access_token()
        refresh_token = current_user.get_patreon_refresh_token()
        try:
            return get_patreon_info_and_make_response(token, refresh_token)
        except Exception as e:
            log.warning(f"problem getting patreon info: {e}")
            if token is not None:
                log.debug(f"token started {token[0:5]}")

    return make_response(jsonify({
        'authenticated_with_patreon': False,
        'user': None
    }))

def get_patreon_info_and_make_response(access_token, refresh_token, update_tokens=False):
    patreon_api = PatreonApi()
    authenticated = False
    user_data = None
    refreshed_tokens = None

    try:
        user_data = patreon_api.get_identity(access_token)
        authenticated = True
    except HTTPError as e:
        log.debug(e)
        if e.response.status_code == 401:
            refreshed_tokens = patreon_api.refresh_token(refresh_token)
            user_data = patreon_api.get_identity(refreshed_tokens[0])
            authenticated = True
        else:
            raise e

    resp = make_response(jsonify({
        'authenticated_with_patreon': authenticated,
        'user': user_data
    }))

    if refreshed_tokens is not None:
        update_tokens = True
        access_token, refresh_token, lifetime = refreshed_tokens

    if user_data is not None:
        user_patreon_id = user_data.id
        log.debug(f"User patreon id is {user_patreon_id}")
        user = None
        ## ensure user for forgesteel patrons
        if user_patreon_id is not None:
            user = User.find_by_patreon_id(user_patreon_id)

            if user is None:
                log.debug('Creating user')
                new_user = User(name=user_data.email)
                new_user.patreon_email = user_data.email
                new_user.patreon_id = user_patreon_id
                new_user.set_patreon_access_token(access_token)
                new_user.set_patreon_refresh_token(refresh_token)
                db.session.add(new_user)
                db.session.commit()
                user = new_user
            elif update_tokens:
                user.set_patreon_access_token(access_token)
                user.set_patreon_refresh_token(refresh_token)
                db.session.commit()

            if has_warehouse_access(user_data):
                set_access_cookies(resp, create_access_token(identity=user))
                set_refresh_cookies(resp, create_refresh_token(identity=user))

    return resp

def set_th_cookie(resp: Response, name: str, value: str, max_age: int):
    secure = current_app.config['JWT_COOKIE_SECURE']
    same_site = current_app.config['JWT_COOKIE_SAMESITE']
    domain = current_app.config['JWT_COOKIE_DOMAIN']

    log.debug(f"Cookie settings: secure={secure} same_site={same_site} domain={domain}")
    log.debug(f"Setting [{name}] to [{value[0:5]}...]")

    if max_age > 0:
        resp.set_cookie(name, value,
                        max_age=max_age,
                        httponly=True,
                        samesite=same_site,
                        domain=domain,
                        secure=secure)
    else:
        resp.set_cookie(name, value,
                        expires=0,
                        httponly=True,
                        samesite=same_site,
                        domain=domain,
                        secure=secure)

## Start the login process
## Returns the OAuth login url
##  also sets a temporary HTTP-only cookie containing state
@token_handler.post('/th/login/start')
def login_start():
    patreon_api = PatreonApi()
    
    redirect_url = os.getenv('PATREON_OAUTH_REDIRECT_URI')

    state = str(uuid.uuid4())

    url = patreon_api.generate_authorize_url(redirect_url, state)
    
    resp = make_response(jsonify({'authorizationUrl': url}))
    
    set_th_cookie(resp, TEMP_LOGIN_COOKIE_NAME, state, 600)

    return resp

## Ends the login process
##  takes in the searchParams from the SPA given by the Oauth redirect
##  Takes the provided code, verifies the provided state (TODO),
##  and gets a token from the OAuth provider
##  It then validates the token and encrypts it in HTTP-only SECURE (& SameSite=strict) cookie
##
## returns authenticated_with_patreon and user data
@token_handler.post('/th/login/end')
def login_end():
    args = request.get_json()
    state = args['state']
    code = args['code']
    temp_cookie = request.cookies.get(TEMP_LOGIN_COOKIE_NAME)

    if (temp_cookie != state):
        msg = 'Incorrect login state cookie'
        if temp_cookie is None:
            msg = 'Missing login state cookie'
        else:
            log.debug(f"state started {temp_cookie[0:10]}")

        log.warning(msg)
        return make_response(jsonify({'message': 'Invalid Authorization request'}), 400)

    redirect_url = os.getenv('PATREON_OAUTH_REDIRECT_URI')

    patreon_api = PatreonApi()
    try:
        access_token, refresh_token, lifetime = patreon_api.get_token(code, redirect_url)
        resp = get_patreon_info_and_make_response(access_token, refresh_token, update_tokens=True)

        set_th_cookie(resp, TEMP_LOGIN_COOKIE_NAME, '', 0)

        return resp
    except Exception as err:
        body = {
            'authenticated_with_patreon': False,
            'message': str(err)
        }

        return make_response(jsonify(body), 400)


## Refresh current access token and rewrite secure cookies
@token_handler.post("/th/refresh")
@jwt_required()
def refresh():
    patreon_api = PatreonApi()

    refresh_token = current_user.get_patreon_refresh_token()
    access_token, new_refresh_token, lifetime = patreon_api.refresh_token(refresh_token)

    user = User.find_by_patreon_id(current_user.patreon_id)
    if user is None:
        return make_response(jsonify(message="Problem getting user"), 400)
    
    user.set_patreon_access_token(access_token)
    user.set_patreon_refresh_token(new_refresh_token)

    db.session.commit()
    db.session.flush()
    return make_response(jsonify(), 204)


## Delete cookies
@token_handler.post("/th/logout")
@jwt_required()
def logout():
    current_user.set_patreon_access_token(None)
    current_user.set_patreon_refresh_token(None)

    db.session.commit()
    db.session.flush()

    return make_response(jsonify(), 204)
