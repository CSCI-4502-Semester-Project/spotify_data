import pandas as pd
import json
import pbjson

def pipe(playlist_id, playlists_directory, track_features_directory, binary=True):

    '''
    Loads the relevant track features for a playlist into a dataframe
    Each row of dataframe is a tack and the columns are the quantitative features for the track
    All meta-data is thrown away. No scaling is done to the data, all scaling must be done outside of the function

    Args:
        playlist_id (str) : Playlist ID
        playlists_directory (str) : Path to where the playlists are stored. Needs to be exact folder where playlist_id is.
        track_features_directory (str) : Path to where all of the track features data is stored
        binary (bool, optional) : Set to True if features data is '.pbjson'. Set to False if features data is '.json'. True by default

    Raises:
        ValueError: Raises ValueError if the playlist_id is not in the playlists_directory

    Returns:
        pd.DataFrame: Returns a DataFrame of the track features for the given playlist
    '''

    
    #open the playlist file that contains all fo the tracks in the playlist
    f = None
    try:
        f = open(f'{playlists_directory}{playlist_id}')

    except:
        raise ValueError(f'Could not open playlist {playlist_id} in directory {playlists_directory}')


    #Load the track_ids
    try:
        num_tracks = int(f.readline())
        track_ids = [''] * num_tracks
        for i, track in enumerate(f.readlines()):
            track_ids[i] = track.split('\n')[0]

        f.close()
    except:
        f.close()
        return

    #Go through all of the tracks and load the features
    playlist_features = []
    features = None
    for track in track_ids:

        #Open the features file for the given track
        features = None
        try:
            if binary:
                f = open(f'{track_features_directory}{track}.pbjson', 'rb+')
                features = pbjson.load(f)
                f.close()

            else:
                f = open(f'{track_features_directory}{track}.json', 'r+')
                features = json.load(f)
                f.close()

        except:
            features = None
            print(f'Warning --- Could not find features for track_id {track}')

        if features is not None:
            playlist_features.append(features)


    #Get rid of useless meta-data. Only keep stuff we can analyze
    features_df = pd.DataFrame(playlist_features).drop(['type', 'id', 'uri', 'track_href', 'analysis_url'], axis=1)

    return features_df
