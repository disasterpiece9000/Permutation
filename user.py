import spotipy
import spotipy.util as util
from tinydb import TinyDB, Query
import configparser
from datetime import datetime, date, timezone
import dateutil.parser
from track import Track

# Read authentication information from ini file
auth_config = configparser.ConfigParser()
auth_config.read('auth.ini')
auth = auth_config['AUTH']

CLIENT_ID = auth['CLIENT_ID']
CLIENT_SECRET = auth['CLIENT_SECRET']
REDIRECT_URI = auth['REDIRECT_URI']
SCOPE = auth['SCOPE']

# Trim non-essential info in URI
def getURI(uri, delimeter_num):
    # Split URI by ':'
    # delimeter_num ensures that parts[-1] returns the target index of the delimeter
    parts = uri.split(":", delimeter_num)
    # Get the index of the last delimeter
    index = len(uri) - len(parts[-1])
    # Trim the string and return the formatted URI
    return uri[index:]

class User:
    def __init__(user, username):
        # User preferences
        user_config = configparser.ConfigParser()
        user_config.read("users/" + username + "/settings.ini")

        # Account information
        accnt_info = user_config['ACCNT_INFO']

        # Get info and trim if required
        if ":" in accnt_info['username']:
            user.username = getURI(accnt_info['username'], 3)
        else:
            user.username = accnt_info['username']

        if ":" in accnt_info['main_playlist']:
            user.playlist_uri = getURI(accnt_info['main_playlist'], 5)
        else:
            user.playlist_uri = accnt_info['main_playlist']

        if ":" in accnt_info['backup_playlist']:
            user.backup_uri = getURI(accnt_info['backup_playlist'], 5)
        else:
            user.backup_uri = accnt_info['backup_playlist']

        # User settings
        settings_info = user_config['SETTINGS']
        user.song_cap = int(settings_info['song_cap'])
        user.min_days = int(settings_info['min_days'])

        # Playlist data
        user.playlist_data = {}
        user.readPlaylistData
        user.playlist_db = TinyDB("users/" + user.username + "/" + user.username + "_data.json")

        # Store the timestamp of the last song processed
        user.last_listen_time = datetime.now(timezone.utc)

        print("Created user: " + user.username)

    # Authorize for the account specified in the user.py file
    def getToken(user):
        token = util.prompt_for_user_token(user.username, SCOPE, client_id=CLIENT_ID,
                                           client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
        user_token = spotipy.Spotify(auth=token)
        return user_token

    # Read existing playlist and store the data in a nested dict
    def readPlaylistData(user):
        user.playlist_data.clear()

        for track in user.playlist_db:
            user.playlist_data[track['track_id']] = Track(track['track_id'], dateutil.parser.parse(track['date_added']),
                                                          track['name'], track['artist'], track['album'],
                                                          track['listen_count'])
