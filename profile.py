import requests
import json
import time

def get_user_profile(user_id, authorizer, verbose):
    while(True): # need to add loop incase of rate limiting, otherwise it shouldn't really be necessary
        spotify_endpoint = 'https://api.spotify.com/v1/users/{user_id}'

        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(spotify_endpoint.format(user_id=user_id), headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 404:
            print('Error. User {user_id} not found.'.format(user_id=user_id))
            return None
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None

