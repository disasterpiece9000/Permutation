import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser

# Authorize for the account specified in the auth.py file
auth = Auth()
token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                   client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

# Gets paginated results from playlist track list
def getPlaylistTracks(username, id):
    results = sp.user_playlist_tracks(username, id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

all_songs = getPlaylistTracks('oh_snap272', '7mJPrlhbnS7ZrWVXO8eWuR')

for song in all_songs:
    print(song['added_at'])
    date_song = dateutil.parser.parse(song['added_at'])
    print(date_song.__str__())
