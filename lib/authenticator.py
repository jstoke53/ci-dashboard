import uuid, urllib, time
from functools import wraps
from datetime import datetime, timedelta
from flask import request, redirect, session, url_for
from lib.clients.itsyouonline import Itsyouonline
from lib.http import HttpStatus

httpStatus = HttpStatus()

class Authenticator:
    def __init__(self, client_id, client_secret, callback_url):
        self.client_id = client_id
        self.organization = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.state = uuid.uuid4().hex[:5]
        self.required_scope = 'user:memberof:{}'.format(self.organization)
        self.auth_url = 'https://itsyou.online/v1/oauth/authorize?'

    def itsyouonline_auth(self):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': self.required_scope,
            'state': self.state
        }
        params = urllib.parse.urlencode(params)
        return redirect(self.auth_url + params)


    def authorize_user(self, code, state):            
        iyo_client = Itsyouonline(client_id=self.client_id,
                                  client_secret=self.client_secret,
                                  callback_url=self.callback_url)

        payload = iyo_client.get_access_token(code, state).json()
        session['username'] = payload['info']['username']
        session['access_token'] = payload['access_token']
        session['is_member_of_org'] = (payload['scope'].strip(',') == self.required_scope)
        session['expires'] = time.time() + payload['expires_in']
    

    def is_authorized_user(self):
        if not self.__is_valid_session():
            return False

        if time.time() > session['expires']:
            return False

        info = {
            'username': session['username'],
            'is_member_of_org': session['is_member_of_org']
        }
        return info

    def __is_valid_session(self):
        if not session:
            return False

        required_keys = ['username', 'access_token', 'is_member_of_org', 'expires']
        return all([x in required_keys for x in session])


    def required_member_of_org(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.__is_valid_session():
                return redirect('/login', code=302) 

            if time.time() > session['expires']:
                return redirect('/login', code=302)

            if not session['is_member_of_org']:
                return redirect('access_denied', code=302)
                
            return func(*args, **kwargs)            
        return decorator


    

        
    

        
    

        
    
