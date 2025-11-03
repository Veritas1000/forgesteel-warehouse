from flask import Blueprint, jsonify
import requests
import os

patreon_oauth = Blueprint('patreon_oauth', __name__)

# https://docs.patreon.com/#step-1-registering-your-client

@patreon_oauth.route('/oauth/redirect')
def oauth_redirect():
    CLIENT_ID = os.getenv('PATREON_CLIENT_ID')
    CLIENT_SECRET = os.getenv('PATREON_CLIENT_SECRET')

    # state = request.args.get('state')
    # code = request.args.get('code')

    # token_response = requests.post(
    #     'https://www.patreon.com/api/oauth2/token',
    #     params={
    #         'grant_type': 'authorization_code',
    #         'code': code,
    #         'client_id': CLIENT_ID,
    #         'client_secret': CLIENT_SECRET,
    #         'redirect_uri': 'http://localhost:5000/oauth/redirect'
    #     },
    #     headers={
    #         'Content-Type': 'application/x-www-form-urlencoded'
    #     }
    # )

    # tokens = token_response.json()
    # access_token = tokens['access_token']
    access_token = os.getenv('TEST_ACCESS_TOKEN')

    user_response = requests.get(
        'https://www.patreon.com/api/oauth2/v2/identity?fields[user]=full_name,email,is_email_verified&include=memberships',
        headers={
            'Authorization': "Bearer {}".format(access_token)
        }
    )
    user = user_response.json()

    campaign_response = requests.get(
        'https://www.patreon.com/api/oauth2/v2/campaigns?fields[campaign]=summary&include=tiers',
        headers={
            'Authorization': "Bearer {}".format(access_token)
        }
    )
    campaigns = campaign_response.json()

    return jsonify({
        'user': user,
        'campaigns': campaigns
        })
