import requests
import base64
import datetime
from urllib.parse import urlencode

client_id = ''
client_secret = ''


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret

        if client_secret == None or client_id == None:
            raise Exception('You must set client_id and client_secret!')

        client_creds = f'{client_id}:{client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_header(self):
        client_creds_b64 = self.get_client_credentials()
        return {'Authorization': f'Basic {client_creds_b64}'}

    def get_token_data(self):
        return {'grant_type': 'client_credentials'}

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_header = self.get_token_header()

        r = requests.post(token_url, data=token_data, headers=token_header)
        if r.status_code not in range(200, 299):
            raise Exception('Authentication Failed!')

        response_data = r.json()
        now = datetime.datetime.now()
        access_token = response_data['access_token']
        expires_in = response_data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()

        if expires < now:
            self.perform_auth()
            return self.get_access_token()

        elif token == None:
            self.perform_auth()
            return self.get_access_token()

        return token

    def search(self, query, search_type='artist', limit=1):
        spotify_access_token = self.get_access_token()
        headers = {'Authorization': f'Bearer {spotify_access_token}'}
        endpoint = 'https://api.spotify.com/v1/search'
        data = urlencode({'q': query, 'type': search_type.lower(), 'limit': limit})
        lookup_url = f'{endpoint}?{data}'
        r = requests.get(lookup_url, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        return r.json()


spotify_client = SpotifyAPI(client_id, client_secret)
print(spotify_client.search('Track Name Here', search_type='Track'))
