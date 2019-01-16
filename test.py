import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser

# Authorize for the account specified in the auth.py file
auth = Auth()
token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                   client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

results = sp.current_user_recently_played(limit=3)
print("Last 10 songs you listened to:\n")

for track in results['items']:
    print("TrackID: " + str(track['played_at']))
