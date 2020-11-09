import requests
import pprint
import json

def track_indexes(track_out, authorizer, verbose):
    href = track_out['href']
    # track_ids = [''] * track_out['total']
    track_ids = []

    index = 0

    while href is not None:
        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(href, headers=headers)

        if response.status_code == 200:
            tracks = response.json()
            for track in tracks['items']:
                if track is None:
                    continue
                if track['track'] is None:
                    continue
                ntrack = track['track']['id']
                track_ids.append(ntrack)
                index += 1
            href = tracks['next']
        elif response.status_code == 404:
            if verbose:
                print('Warning {}: Problem with getting tracks from playlists, verify url {} is correct.'.format(response.status_code, href))
            return None
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None

    return [x for x in track_ids if x is not None] # filters out non values that can sometimes occur

def track_features(tracks, authorizer, verbose):
    spotify_endpoint = 'https://api.spotify.com/v1/audio-features'
    headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}

    remainder = len(tracks)
    offset = 0
    stride = 100
    features = []
    while remainder > 0:
        params = {'ids': ','.join(tracks[offset:offset + stride])} # spotify can only process 100 tracks at a time

        response = requests.get(spotify_endpoint, params=params, headers=headers)

        if response.status_code == 200:
            features += response.json()['audio_features']
            offset += stride
            remainder -= stride
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text))
            return None

    return zip(tracks, features)
