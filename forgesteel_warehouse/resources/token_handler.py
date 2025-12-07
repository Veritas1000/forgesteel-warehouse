import os
import uuid
from flask import Blueprint, jsonify, make_response, request

from forgesteel_warehouse.utils.patreon_api import PatreonApi

token_handler = Blueprint('token_handler', __name__)

TEMP_LOGIN_COOKIE_NAME = 'fs-th-login-temp'
TOKEN_COOKIE_NAME = 'fs-th-token'
TOKEN_REFRESH_COOKIE_NAME = 'fs-th-refresh-token'

## Gets the current session, if present
@token_handler.get('/th/session')
def get_session():
    patreon_api = PatreonApi()
    token = request.cookies.get(TOKEN_COOKIE_NAME)

    logged_in = token is not None

    user_data = None
    if logged_in:
        user_data = patreon_api.get_identity(token)

        ## TODO: refresh tokens as part of this?

    return jsonify({
        'authenticated_with_patreon': logged_in,
        'user': user_data
    })

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
    ## TODO: add 'secure=True' once https is standard
    resp.set_cookie(TEMP_LOGIN_COOKIE_NAME, state, max_age=600, httponly=True)

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
        return make_response(jsonify({'message': 'Invalid Authorization request'}), 400)

    redirect_url = os.getenv('PATREON_OAUTH_REDIRECT_URI')
    
    patreon_api = PatreonApi()
    try:
        access_token, refresh_token, lifetime = patreon_api.get_token(code, redirect_url)
        user_data = patreon_api.get_identity(access_token)

        resp = make_response(jsonify({
            'authenticated_with_patreon': True,
            'user': user_data
        }))
            
        ## TODO: add 'secure=True' once https is standard
        resp.set_cookie(TOKEN_COOKIE_NAME, access_token, max_age=lifetime, httponly=True)
        resp.set_cookie(TOKEN_REFRESH_COOKIE_NAME, refresh_token, max_age=lifetime, httponly=True)
        resp.set_cookie(TEMP_LOGIN_COOKIE_NAME, '', httponly=True, expires=0)
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
    patreon_api = PatreonApi()
    refresh_token = request.cookies.get(TOKEN_REFRESH_COOKIE_NAME)

    access_token, refresh_token, lifetime = patreon_api.refresh_token(refresh_token)
    
    resp = make_response(jsonify(), 204)
    ## TODO: add 'secure=True' once https is standard
    resp.set_cookie(TOKEN_COOKIE_NAME, access_token, max_age=lifetime, httponly=True)
    resp.set_cookie(TOKEN_REFRESH_COOKIE_NAME, refresh_token, max_age=lifetime, httponly=True)

    return resp

## Delete cookies
@token_handler.post('/th/logout')
def logout():
    resp = make_response(jsonify(), 204)
    resp.set_cookie(TOKEN_COOKIE_NAME, '', httponly=True, expires=0)
    resp.set_cookie(TOKEN_REFRESH_COOKIE_NAME, '', httponly=True, expires=0)

    return resp
