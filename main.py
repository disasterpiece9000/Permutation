import spotipy
import spotipy.util as util
from user import User
import dateutil.parser
from datetime import datetime, date, timezone
from tinydb import TinyDB, Query
from tinydb.operations import increment
import time

# Getting things ready
find_stuff = Query()    # Initiate TinyDB Querry
sp = None               # Create Spotify authentication gloabal variable

# Create all user objects
all_users = [User('oh_snap272', '7mJPrlhbnS7ZrWVXO8eWuR', '58keFRFCMhYPRyUvMAX5sR')]

# Check for new songs added to playlist
def checkSongs(user):
    # Get updated tracklist
    current_playlist = getPlaylistTracks(user)

    # Store a list of track IDs in current playlist
    current_tracks = []

    for track in current_playlist:
        track_id = track['track']['id']
        current_tracks.append(track_id)

        # If the track is not in the stored tracklist, then add it
        if track_id not in user.playlist_data:
            date_added = dateutil.parser.parse(track['added_at'])
            listen_count = 0

            user.playlist_data[track_id] = {
                'date_added': date_added, 'listen_count': listen_count}

            user.playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                                'listen_count': listen_count})

            print('New track: ' + track_id + ' found in playlist')

    for track_id in list(user.playlist_data):
        # If the track in the stored list is not in the new list, then remove it
        if track_id not in current_tracks:
            del user.playlist_data[track_id]
            user.playlist_db.remove(find_stuff.track_id == track_id)

            print('Removed track from playlist: ' + track_id)


# Gets paginated results from playlist track list
def getPlaylistTracks(user):
    results = sp.user_playlist_tracks(user.USERNAME, user.playlist_uri)
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    return tracks

# Get recently played songs and log them
def checkRecentlyPlayed(user):
    results = sp.current_user_recently_played(limit=25)

    # Store the new last listen time
    new_last_listen = dateutil.parser.parse(results['items'][0]['played_at'])

    for track in results['items']:
        track_last_played = dateutil.parser.parse(track['played_at'])

        # Log the song if it has not already been counted
        if track_last_played > user.last_listen_time:
            track_id = track['track']['id']
            if track_id in playlist_data:
                logListen(user, track_id)
    # Return the time of the most recently processed song
    return new_last_listen

# Log songs listened to
def logListen(user, track_id):
    # Increment listen count
    user.playlist_data[track_id]['listen_count'] += 1
    user.playlist_db.update(increment('listen_count'), find_stuff.track_id == track_id)

    print('Track: ' + track_id + ' listen count incremented to ' +
          str(user.playlist_data[track_id]['listen_count']))

# Finds the song that has the lowest listens per day ratio
def findLeastListened(user):
    # Save the least listened song's info
    lowest_ratio = 1000.0
    lowest_track_id = None

    for track in user.playlist_data:
        date_added = user.playlist_data[track]['date_added']
        time_delta = datetime.now(timezone.utc) - date_added

        # Don't remove songs if they have been in the playlist for less than 2 weeks
        if time_delta.days > 14:
            listen_ratio = user.playlist_data[track]['listen_count'] / float(time_delta.days)

            if listen_ratio < lowest_ratio:
                lowest_ratio = listen_ratio
                lowest_track_id = track

    if lowest_track_id != None:
        print("Removing track: " + lowest_track_id + " Ratio: " + str(lowest_ratio))
    return lowest_track_id

# Removes least listened to songs until the playlist is at its cap
def trimPlaylist(user):
    while len(user.playlist_data) > 250:
        track = []
        track_id = findLeastListened(user)
        if track_id == None:
            return
        track.append(track_id)

        # Remove the song from the playlist, dict, and database
        sp.user_playlist_remove_all_occurrences_of_tracks(user.USERNAME, user.playlist_uri, track)
        del user.playlist_data[track_id]
        user.playlist_db.remove(find_stuff.track_id == track_id)

        # Add the song to a backup playlist
        sp.user_playlist_add_tracks(user.USERNAME, user.backup_uri, track)

        print('Removed track from playlist: ' + track_id)

# Main method
while(True):
    # Itterate through all users
    for user in all_users:
        sp = user.getToken()
        user.readPlaylistData()

        # Process listens
        try:
            user.last_listen_time = checkRecentlyPlayed(user)
            checkSongs(user)
            trimPlaylist(user)
            time.sleep(10)

        # Fetch a new token when the old one expires
        except spotipy.client.SpotifyException:
            sp = getToken()
            print('Got new token\n')
            continue
