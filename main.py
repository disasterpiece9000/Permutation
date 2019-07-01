import time
import os
import sys
import spotipy
from tinydb import Query
from user import User
from track import Track
import dateutil.parser
from datetime import datetime, timezone
from requests.exceptions import ConnectionError

line = "\n---------------------------------------------------\n"

# Getting things ready
find_stuff = Query()  # Initiate TinyDB Query
sp = None  # Create a global variable for authorized Spotipy
all_users = []  # List of all User objects
path = "./users"  # Path to users folder
folders = os.listdir(path)  # List of all user's folders

# Create all User objects and store in all_users
made_users = False
while not made_users:
    try:
        for username in folders:
            all_users.append(User(username))
            made_users = True
    except ConnectionError:
        print(line + "Connection Error: Sleeping for 1 min" + line)
        time.sleep(60)
        continue


# Read the playlist info and store the tracks in a nested dict/json file
def initialize_playlist(user_obj):
    user_obj.playlist_data.clear()
    user_obj.playlist_db.purge()
    
    playlist = get_playlist_tracks(user_obj)
    for track in playlist:
        track_id = track['track']['id']
        date_added = dateutil.parser.parse(track['added_at'])
        name = track['track']['name']
        artist = track['track']['artists'][0]['name']
        album = track['track']['album']['name']
        listen_count = 0
        
        user_obj.playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                                     'name': name, 'artist': artist, 'album': album,
                                     'listen_count': listen_count})
        
        user_obj.playlist_data[track_id] = Track(track_id, date_added, name, artist, album, listen_count)
    
    print('User: ' + user_obj.username + "\nDatabase generated for playlist")


# Check for new songs added to playlist
def check_songs(user_obj):
    # Get updated tracklist
    current_playlist = get_playlist_tracks(user_obj)
    
    # Store a list of track IDs in current playlist
    current_tracks = []
    for track in current_playlist:
        track_id = track['track']['id']
        current_tracks.append(track_id)
        
        # If a track is in the playlist and not in playlist_data then add it
        if track_id not in user_obj.playlist_data:
            date_added = dateutil.parser.parse(track['added_at'])
            name = track['track']['name']
            artist = track['track']['artists'][0]['name']
            album = track['track']['album']['name']
            listen_count = 0
            
            user.playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
                                     'name': name, 'artist': artist, 'album': album,
                                     'listen_count': listen_count})
            
            user_obj.playlist_data[track_id] = Track(track_id, date_added, name, artist, album, listen_count)
            
            print('User: ' + user_obj.username + '\tNew track found\n\t' +
                  "Name: " + name + "\n\tArtist: " + artist + line)
    
    # If a track in playlist_data is not in the playlist then remove it
    for track_id in list(user_obj.playlist_data):
        if track_id not in current_tracks:
            del user_obj.playlist_data[track_id]
            user_obj.playlist_db.remove(find_stuff.track_id == track_id)


# Gets paginated results from playlist track list
def get_playlist_tracks(user_obj):
    results = sp.user_playlist_tracks(user_obj.username, user_obj.playlist_uri)
    tracks_dict = results['items']
    
    while results['next']:
        results = sp.next(results)
        tracks_dict.extend(results['items'])
    
    return tracks_dict


# Get recently played songs and log them
def check_recently_played(user_obj):
    results = sp.current_user_recently_played(limit=25)
    
    # Store the new last listen time
    try:
        new_last_listen = dateutil.parser.parse(results['items'][0]['played_at'])
    except TypeError:
        print("User: " + user_obj.username + "\tError: Nothing returned for recently played" + line)
        new_last_listen = user_obj.last_listen_time
    
    for track in results['items']:
        track_last_played = dateutil.parser.parse(track['played_at'])
        
        # Log the song if it has not already been counted
        if track_last_played > user_obj.last_listen_time:
            track_id = track['track']['id']
            if track_id in user_obj.playlist_data:
                log_listen(user, track)
    # Return the time of the most recently processed song
    return new_last_listen


# Log songs listened to
def log_listen(user_obj, track_dict):
    track_id = track_dict['track']['id']
    track = user.playlist_data[track_id]
    
    # Increment listen count
    track.listen_count += 1
    user_obj.playlist_db.update({'listen_count': track.listen_count}, find_stuff.track_id == track_id)
    
    print('User: ' + user_obj.username + '\tUpdate listen count\n\t' +
          "Name: " + track.name + "\n\tArtist: " + track.artist + "\nListen Count: " + str(track.listen_count) + line)


# Finds the song that has the lowest listens per day ratio
def find_least_listened(user_obj):
    # Save the least listened song's info
    lowest_ratio = 1000.0
    lowest_track_id = None
    
    for track_id in user_obj.playlist_data:
        track = user_obj.playlist_data[track_id]
        time_delta = datetime.now(timezone.utc) - track.date_added
        
        # Don't remove songs if they have been in the playlist for less than specified days
        if time_delta.days > user_obj.min_days:
            listen_ratio = track.listen_count / float(time_delta.days)
            
            if listen_ratio < lowest_ratio:
                lowest_ratio = listen_ratio
                lowest_track_id = track.id
    return lowest_track_id


# Removes least listened to songs until the playlist is at its cap
def trim_playlist(user_obj):
    while len(user_obj.playlist_data) > user_obj.song_cap:
        track_id = find_least_listened(user_obj)
        if track_id is None:
            return
        track_list = [track_id]
        track = user_obj.playlist_data[track_id]
        
        print('User: ' + user_obj.username + '\tLowest listen song removed\n\t' +
              "Name: " + track.name + "\n\tArtist: " + track.artist)
        
        # Remove the song from the playlist, dict, and database
        sp.user_playlist_remove_all_occurrences_of_tracks(user_obj.username, user_obj.playlist_uri, track_list)
        del user_obj.playlist_data[track_id]
        user_obj.playlist_db.remove(find_stuff.track_id == track_id)
        
        # Add the song to a backup playlist
        if user_obj.backup_uri != "None" and user_obj.backup_uri is not None:
            sp.user_playlist_add_tracks(user_obj.username, user_obj.backup_uri, track_list)
            print("Track added to backup playlist")
        
        print(line)


# Main method
# Initialize a new user
if sys.argv[1] == "init":
    target_user = sys.argv[2]
    for user in all_users:
        # If the user has been created, initialize the playlist data
        if user.username.lower() == target_user.lower():
            sp = user.get_token()
            initialize_playlist(user)
            print(user.username + " was initialized\nExiting now...")
            sys.exit(0)
    
    print("User: " + target_user + "\tThat user was not found. Please make sure they have a folder and .ini file")
    sys.exit(0)

# Run continuously through all users
elif sys.argv[1] == "auto":
    while True:
        try:
            # Iterate through all users
            for user in all_users:
                sp = user.get_token()
                user.read_playlist_data()
                
                # Process listens
                try:
                    user.last_listen_time = check_recently_played(user)
                    check_songs(user)
                    trim_playlist(user)
                    time.sleep(10)
                
                # Fetch a new token when the old one expires
                except spotipy.client.SpotifyException as e:
                    print("Error: " + str(e))
                    continue
        except ConnectionError:
            print("Connection Error: Sleeping for 1 min" + line)
            time.sleep(60)
            continue
