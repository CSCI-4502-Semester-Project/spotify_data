import argparse
import json
import pbjson
import os
from flask import Flask, request
import threading

from profile import get_user_profile
from playlists import get_user_playlists
from authorization import SpotifyAuth
from track import track_indexes, track_features#, track_analysis

app_server = Flask(__name__)
args, auth = None, None # global variables, probably need to change

def get_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('user_id', help='A user\'s Spotify ID.', type=str)
    parser.add_argument('server_url', help='URL for spotify authentication. `127.0.0.1` by default.', type=str, nargs='?', default='127.0.0.1')
    parser.add_argument('redirect_uri', help='Redirect URI used for Spotify Authentication. /callback/ by default.', type=str, nargs='?', default='/callback/')
    parser.add_argument('port', help='Port for redirect URI. 8888 by default', type=int, nargs='?', default='8888')
    parser.add_argument('--profile', help='Get user\'s profile data.', action='store_true')
    parser.add_argument('--playlists', help='Get list of users playlists.', action='store_true')
    parser.add_argument('--features', help='Get features for tracks in playlists. If no playlist data already on disk then --playlist flag required. Use --playlist flag to update playlist data.', action='store_true')
    # parser.add_argument('--analysis', help='Get detailed analysis for tracks in playlists, requires --playlists flag.', action='store_true')
    parser.add_argument('--verbose', help='Increase log output.', action='store_true')
    # parser.add_argument('--culling', help='Cull useless meta-data from the scaped data.', action='store_true') # TODO: implement
    parser.add_argument('--binary', help='Dump json data to binary for space efficiency.', action='store_true')
    parser.add_argument('--pretty', help='Pretty print JSON output. Useful for debugging.', action='store_true')
    args = parser.parse_args()

def authorized_callback():
    global auth, args
    f = open('tokens.jsonc', mode='r+')
    tkn = json.load(f)
    dump_directory = tkn['dump_directory']

    playlists, playlist_track_ids = None, None

    if args.profile:
        profile = get_user_profile(args.user_id, auth, args.verbose)

        if profile:
            out_dir = dump_directory + '{user_id}/'.format(user_id=args.user_id)
            if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
            if args.binary:
                out_file = open(out_dir+'profile.pbjson', 'wb+')
                out_file.truncate(0)
                out_file.write(pbjson.dumps(profile))
                out_file.close()

            else:
                out_file = open(out_dir+'profile.json', 'w+')
                out_file.truncate(0)
                
                if args.pretty:
                    out_file.write(json.dumps(profile, indent=4))
                else:
                    out_file.write(json.dumps(profile))
                
                out_file.close()

    if args.playlists:
        playlists = get_user_playlists(args.user_id, auth, args.verbose)

        if playlists:
            if args.binary:
                out_dir = dump_directory + '{user_id}/'.format(user_id=args.user_id)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                out_file = open(out_dir+'playlists.pbjson', 'wb+')
                out_file.truncate(0)
                out_file.write(pbjson.dumps(playlists))
                out_file.close()
            else:
                out_dir = dump_directory + '{user_id}/'.format(user_id=args.user_id)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                out_file = open(out_dir+'playlists.json', 'w+')
                
                if args.pretty:
                    out_file.write(json.dumps(playlists, indent=4))
                else:
                    out_file.write(json.dumps(playlists))
                out_file.close()

    if args.features:
        # if not pulling new playlist data from spotify, load from disk
        if not args.playlists:
            playlists = None
            try:
                f = open(dump_directory + '{}/{}'.format(args.user_id, 'playlists.pbjson'), 'r')
                playlists = pbjson.loads(f)
            except:
                try:
                    f = open(dump_directory + '{}/{}'.format(args.user_id, 'playlists.json'), 'r')
                    playlists = json.loads(f)
                except:
                    raise IOError('No playlist json data found. Need to get playlist data with --playlists flag for this user.')
        
        # create dict for track indexes
        if playlist_track_ids is None:
            playlist_track_ids = {}

        if not os.path.exists(dump_directory + 'track_features/'):
            os.makedirs(dump_directory + 'track_features/')

        # get all track id's
        for playlist in playlists['items']:
            track_ids = track_indexes(playlist['tracks'], auth, args.verbose)
            if track_ids is None:
                continue

            playlist_track_ids[playlist['id']] = track_ids

            # dump track indexes
            filename = '{}.INDEX'.format(playlist['id'])

            # if we have playlist data then we know that directory exists
            out_file = open('{}{}/{}'.format(dump_directory, args.user_id, filename), 'w+')
            out_file.truncate(0)
            out_file.write('%d\n' % len(track_ids))
            out_file.write('\n'.join(track_ids))
            out_file.close()

            # get track features
            t_features = track_features(track_ids, auth, args.verbose)

            for track_id, features in t_features:
                out_file = open('{}track_features/{}.{}'.format(dump_directory, track_id, 'pbjson' if args.binary else 'json'), 'wb+' if args.binary else 'w+')
                out_file.truncate(0)
                if args.binary:
                    out_file.write(pbjson.dumps(features))
                else:
                    if args.pretty:
                        out_file.write(json.dumps(features, indent=4))
                    else:
                        out_file.write(json.dumps(features))
                out_file.close()

    # if args.analysis:
    #     pass

def flask_thread():
    if args.server_url:
        app_server.run(host=args.server_url, port=args.port)

if __name__ == '__main__':
    get_args() # parse args
    threading.Thread(target=flask_thread).start() # start server for callback

    auth = SpotifyAuth('http://' + args.server_url + ':' + str(args.port) + args.redirect_uri)
    auth.authorize()

    # after authentication call is sent, Spotify will send back an authentication_code to the running Flask server
    # if server recieves valid code then data scraping methods will be called automatically
    # hopefully multi-threading doesn't fuck my shit up too bad :(

@app_server.route('/callback/')
def auth_callback():
    auth_code = ''
    try:
        auth_code = request.args['code']
    except:
        return 'Authentication Failure :('
    auth.get_tokens(auth_code)
    authorized_callback()
    return 'Done. Close tab.'