import spotipy
import spotipy.util as util
from tinydb import TinyDB, Query
import configparser
from datetime import datetime, date, timezone
import dateutil.parser

# Read authentication information from ini file
config = configparser.ConfigParser()
config.read('auth.ini')
auth = config['AUTH']

CLIENT_ID = auth['CLIENT_ID']
CLIENT_SECRET = auth['CLIENT_SECRET']
REDIRECT_URI = auth['REDIRECT_URI']
SCOPE = auth['SCOPE']

class User:
    def __init__(user, username, playlist_uri, backup_uri):
        user.USERNAME = username

        # Target playlists
        user.playlist_uri = playlist_uri  # Main playlist: User adds, bot removes
        user.backup_uri = backup_uri      # Backup playlist: Once removed, bot adds

        # Store the timestamp of the last song processed
        user.last_listen_time = datetime.now(timezone.utc)

        # User playlist info
        user.playlist_data = {}
        user.readPlaylistData
        user.playlist_db = TinyDB(user.USERNAME + '_data.json')

    # Userorize for the account specified in the user.py file
    def getToken(user):
        token = util.prompt_for_user_token(user.USERNAME, SCOPE, client_id=CLIENT_ID,
                                           client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
        user_token = spotipy.Spotify(auth=token)

        print('Got token\n')
        return user_token

    # Read existing playlist and store the data in a nested dict
    def readPlaylistData(user):
        user.playlist_data.clear()

        for track in user.playlist_db:
            user.playlist_data[track['track_id']] = {'date_added': dateutil.parser.parse(track['date_added']),
                                                'listen_count': track['listen_count']}

        print('Playlist data read from file\n')

    # Read the playlist info and store the tracks in a nested dict/json file
    def initializePlaylist(user):
        user.playlist_data.clear()
        user.playlist_db.purge()

        playlist = getPlaylistTracks()
        for track in playlist:
            track_id = track['track']['id']
            date_added = dateutil.parser.parse(track['added_at'])
            listen_count = 0

            playlist_data[track_id] = {'date_added': date_added, 'listen_count': listen_count}

            playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                                'listen_count': listen_count})

        print('Database generated for playlist\n')
