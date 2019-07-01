import spotipy
from spotipy import oauth2
import spotipy.util as util
from tinydb import TinyDB
import configparser
from datetime import datetime, timezone
import dateutil.parser
from track import Track

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
    def __init__(self, username):
        # User preferences
        user_config = configparser.ConfigParser()
        user_config.read("users/" + username + "/settings.ini")
        
        # Account information
        accnt_info = user_config['ACCNT_INFO']
        
        # Get info and trim if required
        if ":" in accnt_info['username']:
            self.username = get_uri(accnt_info['username'], 3)
        else:
            self.username = accnt_info['username']
        
        if ":" in accnt_info['main_playlist']:
            self.playlist_uri = get_uri(accnt_info['main_playlist'], 5)
        else:
            self.playlist_uri = accnt_info['main_playlist']
        
        if ":" in accnt_info['backup_playlist']:
            self.backup_uri = get_uri(accnt_info['backup_playlist'], 5)
        else:
            self.backup_uri = accnt_info['backup_playlist']
        
        # User settings
        settings_info = user_config['SETTINGS']
        self.song_cap = int(settings_info['song_cap'])
        self.min_days = int(settings_info['min_days'])
        
        # Playlist data
        self.playlist_data = {}
        self.playlist_db = TinyDB("users/" + self.username + "/" + self.username + "_data.json")
        self.read_playlist_data()
        
        # Store the timestamp of the last song processed
        self.last_listen_time = datetime.now(timezone.utc)
        
        self.sp_oauth = oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
                                            scope=SCOPE)
        self.token_info = self.sp_oauth.get_cached_token()
        if not self.token_info:
            auth_url = self.sp_oauth.get_authorize_url(show_dialog=True)
            print(auth_url)
            response = input('Paste the above link into your browser, then paste the redirect url here: ')
            
            code = self.sp_oauth.parse_response_code(response)
            self.token_info = self.sp_oauth.get_access_token(code)
        
        self.access_token = self.token_info['access_token']
        self.token = spotipy.Spotify(auth=self.access_token)
        
        print("Created user: " + self.username)
    
    # Authorize for the account specified in the user.py file
    def get_token(self):
        if self.sp_oauth.is_token_expired(self.token_info):
            self.token_info = self.sp_oauth.refresh_access_token(self.token_info["refresh_token"])
            self.access_token = self.token_info["access_token"]
            self.token = spotipy.Spotify(auth=self.token)
        return self.token
    
    # Read existing playlist and store the data in a nested dict
    def read_playlist_data(self):
        self.playlist_data.clear()
        
        for track in self.playlist_db:
            self.playlist_data[track['track_id']] = Track(track['track_id'], dateutil.parser.parse(track['date_added']),
                                                          track['name'], track['artist'], track['album'],
                                                          track['listen_count'])
