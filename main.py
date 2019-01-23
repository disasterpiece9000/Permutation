import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser
from datetime import datetime, date
from tinydb import TinyDB, Query
from tinydb.operations import increment
import time

# Authorize for the account specified in the auth.py file
auth = Auth()
token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                   client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

# Initiate TinyDB Querry
find_stuff = Query()

# Stored playlist info
playlist_data = {}
playlist_uri = '7mJPrlhbnS7ZrWVXO8eWuR'

# TODO: Add method to main loop that checks for new songs added to playlist
#       Verify that song listens are being correctly logged
#       Verify that last_listen_time is working as intended


# Read the existing playlist and store the tracks in a data structure
def initializePlaylist():
    playlist_data.clear()
    playlist_db = TinyDB('playlist_data.json')
    playlist_db.purge()

    playlist = getPlaylistTracks()
    for track in playlist:
        track_id = track['track']['id']
        date_added = dateutil.parser.parse(track['added_at'])
        listen_count = 0

        playlist_data[track_id] = {
            'date_added': date_added, 'listen_count': listen_count}

        playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(), 'listen_count': listen_count})

# Read existing playlist and data
def readPlaylistData():
    playlist_data.clear()
    playlist_db = TinyDB('playlist_data.json')
    for track in playlist_db:
        playlist_data[track['track_id']] = {'date_added': dateutil.parser.parse(track['date_added']),
                                            'listen_count': track['listen_count']}


# Gets paginated results from playlist track list
def getPlaylistTracks():
    results = sp.user_playlist_tracks(auth.USERNAME, playlist_uri)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


# Get recently played songs and log them
def checkRecentlyPlayed(last_listen_time):
    results = sp.current_user_recently_played(limit=10)

    # Store the new last listen time
    new_last_listen = dateutil.parser.parse(results['items'][0]['played_at'])

    for track in results['items']:
        track_last_played = dateutil.parser.parse(track['played_at'])

        if last_listen_time == None or track_last_played > last_listen_time:
            track_id = track['track']['id']
            if track_id in playlist_data:
                logListen(track_id)
    return new_last_listen

# Log songs listened to
def logListen(track_id):
    playlist_db = TinyDB('playlist_data.json')

    # Increment listen count
    playlist_data[track_id]['listen_count'] += 1
    playlist_db.update(increment('listen_count'), find_stuff.track_id == track_id)

# No last listen time when the bot is initialized
last_listen_time = None

initializePlaylist()

# Main method
while(True):
    last_listen_time = checkRecentlyPlayed(last_listen_time)
    print('Init')
    readPlaylistData()
    print(playlist_data)
    time.sleep(60)
