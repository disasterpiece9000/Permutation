import time
import pyodbc
import spotipy
from spotipy import oauth2
import configparser

# Read authentication information from ini file
auth_config = configparser.ConfigParser()
auth_config.read('auth.ini')
auth = auth_config['AUTH']

USERNAME = auth['USERNAME']
CLIENT_ID = auth['CLIENT_ID']
CLIENT_SECRET = auth['CLIENT_SECRET']
REDIRECT_URI = auth['REDIRECT_URI']
SCOPE = auth['SCOPE']


# Trim non-essential info in URI
def get_uri(uri, delimiter_num):
    # Split URI by ':'
    # delimiter_num ensures that parts[-1] returns the index of the target delimiter
    parts = uri.split(":", delimiter_num)
    # Get the index of the target delimiter
    index = len(uri) - len(parts[-1])
    # Trim the string and return the formatted URI
    return uri[index:]


class User:
    def __init__(self, username, playlist_uri, backup_playlist, song_cap, min_days, lastListenTime, token_info, conn):
        self.username = username
        self.playlist_uri = playlist_uri
        self.backup_playlist = backup_playlist
        self.song_cap = song_cap
        self.min_days = min_days
        self.token_info = token_info
        self.last_listen_time = lastListenTime
        self.playlist_track_IDs = None
        self.conn = conn
        self.sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI, scope=SCOPE)
    
    # Authorize for the account specified in the user.py file
    def get_token(self):
        if self.token_info["expires_at"] is None or self.token_info["expires_at"] < int(time.time() + 600):
            self.token_info = self.sp_oauth.refresh_access_token(self.token_info["refresh_token"])
            cursor = self.conn.cursor()
            update_str = "UPDATE UserInfo " \
                         "SET authToken = ?, tokenExpiration = ? " \
                         "WHERE username = ?"
            cursor.execute(update_str, self.token_info["access_token"], self.token_info["expires_at"], self.username)

        return spotipy.Spotify(auth=self.token_info["access_token"])
