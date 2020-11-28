import json
import os

if __name__ == '__main__':
    f = open('tokens.jsonc', mode='r+')
    tkn = json.load(f)
    in_path = tkn['million_playlists_data']
    out_path = tkn['dump_directory']
    out_name = tkn['dump_name']
    f.close()

    if not os.path.exists(out_path + out_name):
        os.makedirs(out_path + out_name)

    # playlists in this dataset don't have their Spotify UID's, probably for privacy
    # need a way to uniquely identify them, and differentiate between these playlists and others
    # use pid as auto-increment for each playlist and stick `m_` infront to distinguish
    prefix = 'm_'

    for filename in os.listdir(in_path):
        if filename.endswith('.json'):
            f = open(in_path + filename)
            playlist_slice = json.load(f)['playlists']
            f.close()

            for playlist in playlist_slice:
                num_tracks = playlist['num_tracks']
                pid = playlist['pid']
                f = open(out_path + out_name + f'\\{prefix}{pid}.INDEX', 'w+')
                f.truncate(0)
                f.write(f'{num_tracks}\n')
                for track in playlist['tracks']:
                    f.write(f'{track["track_uri"].split(":")[2]}\n')
                f.close()

