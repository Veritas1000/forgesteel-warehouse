
from dataclasses import dataclass, field
from datetime import date, datetime
import logging
import os
from typing import List
from urllib.parse import urlencode
import requests

log = logging.getLogger(__name__)

# ## Useful for debugging low level http requests
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

class PatreonApi:
    _requested_token_scopes = [
        'identity.memberships'
    ]

    _identity_includes = [
        'memberships.campaign',
        'memberships.currently_entitled_tiers'
    ]
    _member_fields = [
        'patron_status',
        'currently_entitled_amount_cents',
        'pledge_relationship_start',
    ]
    _user_fields = ['email']
    _campaign_fields = ['url']
    _tier_fields = ['title']

    def __init__(self):
        self.CLIENT_ID = os.getenv('PATREON_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('PATREON_CLIENT_SECRET')
        self.MCDM_CAMPAIGN_ID = os.getenv('PATREON_CAMPAIGN_ID_MCDM')
        self.FORGESTEEL_CAMPAIGN_ID = os.getenv('PATREON_CAMPAIGN_ID_FORGESTEEL')

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
            msg = self._get_error_msg(response)
            raise Exception(f"Error communicating with Patreon: {msg}")

    def _get_error_msg(self, response):
        err = response.json()
        msg = 'Unknown error'
        if 'error_description' in err:
            msg = err['error_description']
        elif 'title' in err:
            msg = err['title']
        return msg

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
            msg = self._get_error_msg(response)
            raise Exception(f"Error communicating with Patreon: {msg}")

    def get_identity(self, access_token):
        response = requests.get(
            'https://www.patreon.com/api/oauth2/v2/identity',
            params = {
                'include': ','.join(self._identity_includes),
                'fields[member]': ','.join(self._member_fields),
                'fields[user]': ','.join(self._user_fields),
                'fields[campaign]': ','.join(self._campaign_fields),
                'fields[tier]': ','.join(self._tier_fields),
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
            msg = self._get_error_msg(response)
            raise Exception(f"Error communicating with Patreon: {msg}")

    def _parse_identity_response(self, identity_json):
        patreon_id = None
        patreon_email = None

        if identity_json is not None and 'data' in identity_json:
            if 'id' in identity_json['data']:
                patreon_id = identity_json['data']['id']

            if 'attributes' in identity_json['data'] and 'email' in identity_json['data']['attributes']:
                patreon_email = identity_json['data']['attributes']['email']

        forgesteel_state = PatronState()
        mcdm_state = PatronState()

        ## find the campaigns we care about
        if identity_json is not None and 'included' in identity_json:
            memberships = list(filter(lambda inc: inc['type'] == 'member'
                                        and 'relationships' in inc
                                        and 'campaign' in inc['relationships']
                                        and 'currently_entitled_tiers' in inc['relationships']
                                        and 'data' in inc['relationships']['campaign']
                                        and 'id' in inc['relationships']['campaign']['data'],
                                        identity_json['included'])
                                    )
            
            tiers = list(filter(lambda inc: inc['type'] == 'tier',
                                identity_json['included'])
                            )
            tier_map = dict(map(lambda tier: (tier['id'], tier['attributes']['title']), tiers))

            forgesteel_state = self._get_patron_state(self.FORGESTEEL_CAMPAIGN_ID, memberships, tier_map)
            mcdm_state = self._get_patron_state(self.MCDM_CAMPAIGN_ID, memberships, tier_map)

        return PatreonUser(
            id=patreon_id,
            email=patreon_email,
            forgesteel=forgesteel_state,
            mcdm=mcdm_state
        )
    
    def _get_patron_state(self, campaign_id, memberships, all_tiers):
        patron_state = PatronState()
        
        for membership in memberships:
            if membership['relationships']['campaign']['data']['id'] == campaign_id:
                patron_state.patron = membership['attributes']['patron_status'] == 'active_patron'
                
                if patron_state.patron:
                    tiers = list(t['id'] for t in membership['relationships']['currently_entitled_tiers']['data'])
                    patron_state.tiers = list(map(lambda t: PatronTier(id=t, title=all_tiers.get(t)), tiers))
                    patron_state.tier_cents = membership['attributes']['currently_entitled_amount_cents']
                    patron_state.start = datetime.fromisoformat(membership['attributes']['pledge_relationship_start']).date()

        return patron_state

@dataclass
class PatronTier:
    id: str
    title: str

@dataclass
class PatronState:
    patron: bool = False
    tiers: List[PatronTier] = field(default_factory=lambda: [])
    tier_cents: int = 0
    start: date | None = None

@dataclass
class PatreonUser:
    id: str | None = None
    email: str | None = None
    forgesteel: PatronState | None = None
    mcdm: PatronState | None = None
