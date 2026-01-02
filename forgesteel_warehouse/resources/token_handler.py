import logging
import os
import uuid
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies

from forgesteel_warehouse import db
from forgesteel_warehouse.models import User
from forgesteel_warehouse.utils.patreon_api import PatreonApi

token_handler = Blueprint('token_handler', __name__)

log = logging.getLogger(__name__)

TEMP_LOGIN_COOKIE_NAME = 'fs-th-login-temp'
TOKEN_COOKIE_NAME = 'fs-th-token'
TOKEN_REFRESH_COOKIE_NAME = 'fs-th-refresh-token'

## Gets the current session, if present
@token_handler.get('/th/session')
def get_session():
    token = request.cookies.get(TOKEN_COOKIE_NAME)

    try:
        return get_patreon_info_and_make_response(token)
    except:
        return make_response(jsonify({
            'authenticated_with_patreon': False,
            'user': None
        }))

def get_patreon_info_and_make_response(access_token):
    patreon_api = PatreonApi()
    user_data = patreon_api.get_identity(access_token)

    resp = make_response(jsonify({
        'authenticated_with_patreon': True,
        'user': user_data
    }))

    user_patreon_id = user_data.id
    user = None
    ## ensure user for forgesteel patrons
    if user_patreon_id is not None \
            and user_data.forgesteel is not None \
            and user_data.forgesteel.patron is True:
        user = User.find_by_patreon_id(user_patreon_id)

        if user is None:
            new_user = User(name=user_data.email)
            new_user.patreon_email = user_data.email
            new_user.patreon_id = user_patreon_id
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        
        wh_access_token = create_access_token(identity=user)
        wh_refresh_token = create_refresh_token(identity=user)
        set_access_cookies(resp, wh_access_token)
        set_refresh_cookies(resp, wh_refresh_token)

    return resp

def set_th_cookie(resp: Response, name: str, value: str, max_age: int):
    ## TODO: enable samesite once co-hosted with app
    ##       might also be able to remove partitioned then
    if max_age > 0:
        resp.set_cookie(name, value,
                        max_age=max_age,
                        httponly=True,
                        samesite='None',
                        secure=True,
                        partitioned=True)
    else:
        resp.set_cookie(name, value,
                        expires=0,
                        httponly=True,
                        samesite='None',
                        secure=True,
                        partitioned=True)

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
    # resp.set_cookie(TEMP_LOGIN_COOKIE_NAME, state, max_age=600, httponly=True, samesite='None', secure=True, partitioned=True)

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
        msg = 'Missing login state cookie' if temp_cookie is None else 'Incorrect login state cookie'
        log.warning(msg)
        return make_response(jsonify({'message': 'Invalid Authorization request'}), 400)

    redirect_url = os.getenv('PATREON_OAUTH_REDIRECT_URI')
    
    patreon_api = PatreonApi()
    try:
        access_token, refresh_token, lifetime = patreon_api.get_token(code, redirect_url)
        resp = get_patreon_info_and_make_response(access_token)

        set_th_cookie(resp, TOKEN_COOKIE_NAME, access_token, lifetime)
        set_th_cookie(resp, TOKEN_REFRESH_COOKIE_NAME, refresh_token, lifetime)
        set_th_cookie(resp, TEMP_LOGIN_COOKIE_NAME, '', 0)

        return resp
    except Exception as err:
        body = {
            'authenticated_with_patreon': False,
            'message': str(err)
        }

        return make_response(jsonify(body), 400)

## Refresh current access token and rewrite secure cookies
@token_handler.post('/th/refresh')
def refresh():
    refresh_token = request.cookies.get(TOKEN_REFRESH_COOKIE_NAME)
    patreon_api = PatreonApi()

    access_token, refresh_token, lifetime = patreon_api.refresh_token(refresh_token)
    
    resp = make_response(jsonify(), 204)
    set_th_cookie(resp, TOKEN_COOKIE_NAME, access_token, lifetime)
    set_th_cookie(resp, TOKEN_REFRESH_COOKIE_NAME, refresh_token, lifetime)

    return resp

## Delete cookies
@token_handler.post('/th/logout')
def logout():
    resp = make_response(jsonify(), 204)
    set_th_cookie(resp, TOKEN_COOKIE_NAME, '', 0)
    set_th_cookie(resp, TOKEN_REFRESH_COOKIE_NAME, '', 0)

    return resp
