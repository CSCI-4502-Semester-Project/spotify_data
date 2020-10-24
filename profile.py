import requests
import json

def get_user_profile(user_id, authorizer, verbose):
    spotify_endpoint = 'https://api.spotify.com/v1/users/{user_id}'

    headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
    response = requests.get(spotify_endpoint.format(user_id=user_id), headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print('Error. User {user_id} not found.'.format(user_id=user_id))
        return None
    else:
        print('Error %d' % response.status_code)
        if verbose:
            print(json.loads(response.text)['error']['message'])
        return None

