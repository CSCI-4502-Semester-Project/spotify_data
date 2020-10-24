Scripts for scraping spotify data from API

Right now it can pull profile data, playlist data, and track features data.

Before you run scripts you need a `tokens.jsonc` file in same directory as scipts

    {
        "dump_directory": <Directory where scraped data will be written to>,
        "client_id": <Client ID token from Spotify>,
        "client_secret": <Client Secret token from Spotify>
    }

To get ID and Secret token you need to make an app on https://developer.spotify.com/dashboard/login

Once you have made the app you need to set callback URLs so that the scripts can automatically authorize themselves. Click on `Edit Settings` then add a website and redirect URI. I have mine set to http://localhost:8888 and http://127.0.0.1:8888/callback/ respectively.

To run the scipts you need to install `Flask` and `pbjson`, they can be installed with pip.

When you run the scripts you have to specify args to say what data you want. Use -h to see all of them. Most importantly you need to set `server_url`, `redirect_uri`, and `port`. These need to be set so that they exactly match the redirect url you set in the spotify app settings. So for http://127.0.0.1:8888/callback/ you would set `server_url = 127.0.0.1`, `redirect_uri = /callback/`, and `port = 8888`, you do not include the http:// part. There are defaults, and it defaults to the values just listed.

To get all data for a user you would use:
    
    python dump_user_data.py [user_id] --profile --playlists --features --binary --verbose

This gets profile data, playlist data, and all of the track feature data for the the user's playlists.

Generated output file structure:

    ./
    |
    +---[user_id]
    |   |
    |   |   profile         (.json / .pbjson)
    |   |   playlists       (.json / .pbjson)
    |   |   *playlist_index (.INDEX)
    |
    +---track_features
    |   |   features        (.json / .pbjson)

Inside the root dump folder it will create a new folder for the specified user. In this folder it will put the scraped profile and their playlists metadata, and the track indexes for each playlist. The profile and playlists will be dumped in the `.json` format they arrived in. If the `--binary` flag is used it will dump it into a `.pbjson` file to reduce size. Playlist index files are named after the playlist id attribute, inside the file the first line is the number of tracks in the playlist and every subsequent line is a track ID for a track in the playlist that points to a file in the `track_features` directory.

In the track features directory is the unique list of all track's features from all users that have been scraped. Each file is named after the track ID and contains the features returned from the Spotify API stored in either json or pbjson.
