import requests
import pprint
import json
import time

def track_indexes(track_out, authorizer, verbose):
    href = track_out['href']
    track_ids = [''] * track_out['total']
    track_albums_id = [''] * track_out['total']
    #track_ids = []

    index = 0

    while href is not None:
        headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}
        response = requests.get(href, headers=headers)

        if response.status_code == 200:
            tracks = response.json()
            for track in tracks['items']:
                if track is None or track['track'] is None:
                    continue
                track_ids[index] = track['track']['id']
                track_albums_id[index] = track['track']['album']['id']
                #track_ids.append(ntrack)
                index += 1
            href = tracks['next']
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response.status_code == 404:
            if verbose:
                print('Warning {}: Problem with getting tracks from playlists, verify url {} is correct.'.format(response.status_code, href))
            return None
        else:
            print('Error %d' % response.status_code)
            if verbose:
                print(json.loads(response.text)['error']['message'])
            return None

    filter_Array = []
    filter_Array2 = []
    for x in range(len(track_ids)):
        if track_ids[x] is not None and track_albums_id[x] is not None and track_ids[x] and track_albums_id[x]:
            filter_Array.append(track_ids[x])
            filter_Array2.append(track_albums_id[x])
    return filter_Array, filter_Array2  # filters out none and empty values that can sometimes occur

def track_features(tracks, albums, authorizer, verbose):
    spotify_endpoint = 'https://api.spotify.com/v1/audio-features'
    spotify_endpoint2 = 'https://api.spotify.com/v1/albums'
    headers = {"Accept":"application/json", "Content-Type":"application/json", "Authorization": "Bearer {bearer}".format(bearer=authorizer.bearer)}

    remainder = len(tracks)
    print("number of album ids and track ids ",remainder, len(albums))
    offset = 0
    stride = 20
    features = []
    genres = []
    while remainder > 0:
        params = {'ids': ','.join(tracks[offset:offset + stride])} # spotify can only process 100 tracks at a time
        params2 = {'ids': ','.join(albums[offset:offset + stride])} # can only process 20 albums at a time

        response = requests.get(spotify_endpoint, params=params, headers=headers)
        response2 = requests.get(spotify_endpoint2, params=params2, headers=headers)

        if response.status_code == 200 and response2.status_code == 200:
            try:
                genres += response2.json()['genres']
                print(response2.json()['genres'])
            except:
                for album in response2.json()['albums']:
                    if 'genres' in album:
                        genres += album['genres']
                    else:
                        genres += []
            features += response.json()['audio_features']
            offset += stride
            remainder -= stride
        elif response.status_code == 429:
            limit = int(response.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        elif response2.status_code == 429:
            limit = int(response2.headers['Retry-After'])
            print('Hit rate limit, waiting for {} seconds to continue'.format(limit))
            time.sleep(limit)
        else:
            # print('Error %d' % response.status_code)
            print('Error %d' % response2.status_code)
            if verbose:
                # print(json.loads(response.text))
                print(json.loads(response2.text))

            return None

    pprint.pprint(genres)
    return zip(tracks, features)
