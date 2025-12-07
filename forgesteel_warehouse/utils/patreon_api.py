
from dataclasses import dataclass
from datetime import date, datetime
import json
import logging
import os
from urllib.parse import urlencode
import requests

log = logging.getLogger(__name__)

## Useful for debugging low level http requests
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

class PatreonApi:
    _requested_token_scopes = [
        'identity',
        'identity[email]',
        'identity.memberships',
        'campaigns'
    ]

    _identity_includes = [
        'memberships',
        'campaign',
        'memberships.campaign'
    ]
    _member_fields = [
        'patron_status',
        'currently_entitled_amount_cents',
        'last_charge_status',
        'pledge_relationship_start',
    ]
    _user_fields = ["email"]
    _campaign_fields = ["url"]

    def __init__(self):
        self.CLIENT_ID = os.getenv('PATREON_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('PATREON_CLIENT_SECRET')
        self.MCDM_CAMPAIGN_ID = os.getenv('PATREON_CAMPAIGN_ID_MCDM')

    def generate_authorize_url(self, redirect_uri, state):
        params = {
            'response_type': 'code',
            'client_id': self.CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(self._requested_token_scopes),
            'state': state,
        }
        url = f"https://www.patreon.com/oauth2/authorize?{urlencode(params)}"
        return url

    def get_token(self, auth_code, redirect_uri):
        response = requests.post(
            'https://www.patreon.com/api/oauth2/token',
            params = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
                'redirect_uri': redirect_uri
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout = 10
        )

        if response.ok:
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            lifetime = tokens['expires_in']
            return access_token, refresh_token, lifetime
        else:
            err = response.json()
            raise Exception(f"Error communicating with Patreon: {err['error_description']}")

    def refresh_token(self, refresh_token):
        response = requests.post(
            'https://www.patreon.com/api/oauth2/token',
            params = {
                'grant_type': 'refresh_token',
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
                'refresh_token': refresh_token
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout = 10
        )

        if response.ok:
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            lifetime = tokens['expires_in']
            return access_token, refresh_token, lifetime
        else:
            err = response.json()
            raise Exception(f"Error communicating with Patreon: {err['error_description']}")

    def get_identity(self, access_token):
        response = requests.get(
            'https://www.patreon.com/api/oauth2/v2/identity',
            params = {
                'include': self._identity_includes,
                'fields[member]': ','.join(self._member_fields),
                'fields[user]': ','.join(self._user_fields),
                'fields[campaign]': ','.join(self._campaign_fields),
            },
            headers = {
                'Authorization': f"Bearer {access_token}"
            },
            timeout = 10
        )

        if response.ok:
            identity = response.json()
            return self._parse_identity_response(identity)
        else:
            err = response.json()
            raise Exception(f"Error communicating with Patreon: {err['error_description']}")

    def _parse_identity_response(self, identity_json):
        mcdm_state = PatronState(patron=False, tier_cents=0, start=None)

        # Find the mcdm campaign
        try:
            memberships = list(filter(lambda inc: inc['type'] == 'member' and inc['id'] == self.MCDM_CAMPAIGN_ID, identity_json['included']))
            if len(memberships) > 0:
                membership = memberships[0]
                mcdm_state.patron = membership['attributes']['patron_status'] == 'active_patron'
                if mcdm_state.patron:
                    mcdm_state.tier_cents = membership['attributes']['currently_entitled_amount_cents']
                    mcdm_state.start = datetime.fromisoformat(membership['attributes']['pledge_relationship_start']).date()
        except:
            pass

        return PatreonUser(mcdm=mcdm_state)

@dataclass
class PatronState:
    patron: bool
    tier_cents: int
    start: date | None

@dataclass
class PatreonUser:
    mcdm: PatronState
