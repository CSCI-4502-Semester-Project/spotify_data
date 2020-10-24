import requests
import json

def get_user_playlists(user_id, authorizer, verbose):
    spotify_endpoint = 'https://api.spotify.com/v1/users/{user_id}/playlists'

    # there's a limit to the number of playlists that can be downloaded at a time
    # keep downloading playlists until we run out (next = null)
    playlists = {'items':None} 
    while True:
        params = {'limit': 50}
        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(spotify_endpoint.format(user_id=user_id), headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if playlists['items'] is None:
                playlists['items'] = data['items']
            else:
                playlists['items'] += data['items']
            
            if data['next'] is None:
                return playlists
            else:
                spotify_endpoint = data['next']
        elif response.status_code == 404:
            print('Error. User {user_id} not found.'.format(user_id=user_id))
            return None
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None