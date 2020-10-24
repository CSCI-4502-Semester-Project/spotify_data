import requests
import json
import random
import webbrowser
import base64

class SpotifyAuth():
    def __init__(self, redirect):
        f = open('tokens.jsonc', mode='r+')
        tkn = json.load(f)

        self.authorization_token = ''
        self.bearer = ''
        self.refresh_token = ''

        self.client_id = tkn['client_id']
        self.client_secret = tkn['client_secret']

        self.redirect = redirect
    
    def generate_rand_string(self, length):
        return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=length))

    def authorize(self, *scope):
        spotify_endpoint = 'https://accounts.spotify.com/authorize'
        state = self.generate_rand_string(16)
        params = {  'client_id':self.client_id,
                    'response_type':'code',
                    'redirect_uri':self.redirect,
                    'state':state,
                    'scope':' '.join(scope)}
        
        response = requests.get(spotify_endpoint, params=params)

        if response.status_code == 200:
            webbrowser.open(response.url, new=2)
        else:
            print('Authorization Error {code}'.format(code=response.status_code))
    
    def get_tokens(self, auth_code):
        spotify_endpoint = 'https://accounts.spotify.com/api/token'
        params = {  'grant_type':'authorization_code',
                    'code':auth_code,
                    'redirect_uri':self.redirect}
        enc = base64.b64encode(("{}:{}".format(self.client_id, self.client_secret)).encode())
        headers = {"Authorization": "Basic {}".format(enc.decode()), "Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(spotify_endpoint, params=params, headers=headers)

        if response.status_code == 200:
            self.bearer = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
        else:
           print(response.text)
           return 'Error.'
    
    def refresh(self):
        spotify_endpoint = 'https://accounts.spotify.com/api/token'
        params = {  'grant_type':'refresh_token',
                    'refresh_token':self.refresh_token}
        enc = base64.b64encode(("{}:{}".format(self.client_id, self.client_secret)).encode())
        headers = {"Authorization": "Basic {}".format(enc.decode()), "Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(spotify_endpoint, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
           print(response.text)
           return None