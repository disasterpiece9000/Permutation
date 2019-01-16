import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser
from datetime import datetime, date

# Authorize for the account specified in the auth.py file
auth = Auth()
token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                   client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

playlist_data = {}

# TODO: figure out how to rank songs by date added and number of listens
#       create loop to find new listens
#       create logListen() func to update playlist_data
#       handel new_last_listen var in checkRecentlyPlayed()


# Read the existing playlist and store the tracks in a data structure
# Nested dict? {track_id: {date_added:x, listen_count:y}}
def initializePlaylist(playlistID):
    playlist = getPlaylistTracks(auth.USERNAME, playlistID)
    for track in playlist:
        track_id = track['track']['id']
        date_added = datetime.now()
        listen_count = 0

        playlist_data[track_id] = {
            'date_added': date_added, 'listen_count': listen_count}

# Gets paginated results from playlist track list
def getPlaylistTracks(username, id):
    results = sp.user_playlist_tracks(username, id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results['items'])
        tracks.extend(results['items'])
    return tracks


# Get recently played songs and log them
def checkRecentlyPlayed(last_listen_time):
    results = sp.current_user_recently_played(limit=10)

    # Store the new last listen time
    new_last_listen = dateutil.parser.parse(results['items'][0]['played_at'])

    for track in results['items']:
        track_last_played = dateutil.parser.parse(track['played_at'])

        if track_last_played > last_listen_time:
            track_name = track['track']['name']
            track_id = track['track']['id']
            logListen(track)
