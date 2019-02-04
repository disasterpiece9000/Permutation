import spotipy
import spotipy.util as util
from user import User
import dateutil.parser
import configparser

# Read authentication information from ini file
auth_config = configparser.ConfigParser()
auth_config.read('auth.ini')
auth = auth_config['AUTH']

CLIENT_ID = auth['CLIENT_ID']
CLIENT_SECRET = auth['CLIENT_SECRET']
REDIRECT_URI = auth['REDIRECT_URI']
SCOPE = auth['SCOPE']

token = util.prompt_for_user_token('oh_snap272', SCOPE, client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

# Gets paginated results from playlist track list
results = sp.user_playlist_tracks('oh_snap272', '7mJPrlhbnS7ZrWVXO8eWuR')
tracks = results['items']

for track in tracks:
    print(track['track']['name'])
    print(track['track']['album']['name'])
