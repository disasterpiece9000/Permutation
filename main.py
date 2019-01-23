import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser
from datetime import datetime, date
from tinydb import TinyDB, Query
from tinydb.operations import increment
import time

auth = Auth()

# Initiate TinyDB Querry
find_stuff = Query()

# Stored playlist info
playlist_data = {}
playlist_uri = '7mJPrlhbnS7ZrWVXO8eWuR'

# TODO: Add method to main loop that checks for new songs added to playlist


# Authorize for the account specified in the auth.py file
def getToken():
    auth = Auth()
    token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                        client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
    return spotipy.Spotify(auth=token)

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

# Check for new songs added to playlist
def checkNewSongs():
    # Get updated tracklist
    current_playlist = getPlaylistTracks()

    for track in current_playlist:
        track_id = track['track']['id']

        # If the track is not in the stored tracklist, then add it
        if track_id not in playlist_data:
            date_added = dateutil.parser.parse(track['added_at'])
            listen_count = 0

            playlist_data[track_id] = {
                'date_added': date_added, 'listen_count': listen_count}

            playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(), 'listen_count': listen_count})


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

        # Log the song if it has not already been counted
        if last_listen_time == None or track_last_played > last_listen_time:
            track_id = track['track']['id']
            if track_id in playlist_data:
                logListen(track_id)
    # Return the time of the most recently processed song
    return new_last_listen

# Log songs listened to
def logListen(track_id):
    playlist_db = TinyDB('playlist_data.json')

    # Increment listen count
    playlist_data[track_id]['listen_count'] += 1
    playlist_db.update(increment('listen_count'), find_stuff.track_id == track_id)

    print('Track: ' + track_id + ' listen count incremented')

# No last listen time when the bot is initialized
last_listen_time = None

sp = getToken()
readPlaylistData()

# Main method
while(True):
    try:
        last_listen_time = checkRecentlyPlayed(last_listen_time)
        checkNewSongs()
        time.sleep(10)

    # Fetch a new token when the old one expires
    except spotipy.client.SpotifyException:
        sp = getToken()
        print('Got new token')
        continue
