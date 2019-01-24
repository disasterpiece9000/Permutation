import spotipy
import spotipy.util as util
from auth import Auth
import dateutil.parser
from datetime import datetime, date, timezone
from tinydb import TinyDB, Query
from tinydb.operations import increment
import time

# TODO: DEBUG EVERYTHING

# Import auth info
auth = Auth()

# Initiate TinyDB Querry
find_stuff = Query()

# Stored playlist info
playlist_data = {}
playlist_uri = '7mJPrlhbnS7ZrWVXO8eWuR'

# Authorize for the account specified in the auth.py file
def getToken():
    auth = Auth()
    token = util.prompt_for_user_token(auth.USERNAME, auth.SCOPE, client_id=auth.CLIENT_ID,
                                       client_secret=auth.CLIENT_SECRET, redirect_uri=auth.REDIRECT_URI)
    auth_token = spotipy.Spotify(auth=token)

    print('Got token\n')
    return auth_token

# Read the playlist info and store the tracks in a nested dict/json file
def initializePlaylist():
    playlist_data.clear()
    playlist_db = TinyDB('playlist_data.json')
    playlist_db.purge()

    playlist = getPlaylistTracks()
    for track in playlist:
        track_id = track['track']['id']
        date_added = dateutil.parser.parse(track['added_at'])
        listen_count = 0

        playlist_data[track_id] = {'date_added': date_added, 'listen_count': listen_count}

        playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                            'listen_count': listen_count})

    print('Database generated for playlist\n')

# Read existing playlist and store the data in a nested dict
def readPlaylistData():
    playlist_data.clear()
    playlist_db = TinyDB('playlist_data.json')

    for track in playlist_db:
        playlist_data[track['track_id']] = {'date_added': dateutil.parser.parse(track['date_added']),
                                            'listen_count': track['listen_count']}

    print('Playlist data read from file\n')

# Check for new songs added to playlist
def checkNewSongs():
    # Get updated tracklist
    current_playlist = getPlaylistTracks()

    for track in current_playlist:
        track_id = track['track']['id']

        # If the track is not in the stored tracklist, then add it
        if track_id not in playlist_data:
            playlist_db = TinyDB('playlist_data.json')
            date_added = dateutil.parser.parse(track['added_at'])
            listen_count = 0

            playlist_data[track_id] = {
                'date_added': date_added, 'listen_count': listen_count}

            playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                                'listen_count': listen_count})

            print('New track: ' + track_id + ' found in playlist')


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
        if track_last_played > last_listen_time:
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

    print('Track: ' + track_id + ' listen count incremented to ' +
          str(playlist_data[track_id]['listen_count']))

# Finds the song that has the lowest listens per day ratio
def findLeastListened():
    # Save the least listened song's info
    lowest_ratio = 100.0
    lowest_track_id = None

    for track in playlist_data:
        date_added = playlist_data[track]['date_added']
        time_delta = datetime.now(timezone.utc) - date_added

        # Don't remove songs if they have been in the playlist for less than 2 weeks
        if time_delta.days > 0:
            listen_ratio = playlist_data[track]['listen_count'] / float(time_delta.days)

            if listen_ratio < lowest_ratio:
                lowest_ratio = listen_ratio
                lowest_track_id = track

    print("Removing track: " + lowest_track_id + " Ratio: " + str(lowest_ratio))
    return lowest_track_id

# Removes least listened to songs until the playlist is at its cap
def trimPlaylist():
    while len(playlist_data) > 250:
        playlist_db = TinyDB('playlist_data.json')
        track = []
        track_id = findLeastListened()
        if track_id == None:
            return
        track.append(track_id)

        # Remove the song from the playlist, dict, and database
        sp.user_playlist_remove_all_occurrences_of_tracks(auth.USERNAME, playlist_uri, track)
        del playlist_data[track_id]
        playlist_db.remove(find_stuff.track_id == track_id)

        print('Removed track from playlist: ' + track_id)



sp = getToken()
readPlaylistData()
#initializePlaylist()

# No last listen time when the bot is initialized
last_listen_time = datetime.now(timezone.utc)

# Main method
while(True):
    try:
        last_listen_time = checkRecentlyPlayed(last_listen_time)
        checkNewSongs()
        trimPlaylist()
        time.sleep(10)

    # Fetch a new token when the old one expires
    except spotipy.client.SpotifyException:
        sp = getToken()
        print('Got new token\n')
        continue
