import uuid, urllib, time, requests
from lib.tools import Tools

provider_scopes = {
    'github':'',
    'itsyouonline':'user,organizations'
}

class OAuth2:
    def __init__(self):
        self.tools = Tools()
        self.config = self.tools.read_config()
        self.provider = self.config['oauth2']['provider']
        self.client_id = self.config['oauth2']['client_id']
        self.client_secret = self.config['oauth2']['client_secret']
        self.callback_url = self.config['oauth2']['callback_url']
        self.auth_url = self.config['oauth2']['auth_url']
        self.token_url = self.config['oauth2']['token_url']
        
    def get_auth_url(self):
        scope = provider_scopes[self.provider]
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': scope,
            'state': 'xxxx'
        }
        params = urllib.parse.urlencode(params)
        return self.auth_url + '?' + params

        
    def get_access_token(self, code, state):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.callback_url,
            'code': code,
            'state': 'xxxx'
        }
        headers = {'Accept':'application/json'}
        response = requests.post(self.token_url, params=params, headers=headers)
        return response