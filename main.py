import time
import sys
import spotipy
import pyodbc
from user import User
import dateutil.parser
from datetime import datetime, timezone
from requests.exceptions import ConnectionError

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=permutation2.c06ndc8a9kh3.us-east-1.rds.amazonaws.com,1433;'
                      'uid=admin;'
                      'pwd=password;'
                      'Database=Permutation;'
                      'Trusted_Connection=no;',
                      autocommit=True)
cursor = conn.cursor()

line = "\n---------------------------------------------------\n"

# Getting things ready
sp = None  # Create a global variable for authorized Spotipy
all_users = []  # List of all User objects


# Create all User objects and store in all_users
def get_all_users():
    all_users.clear()
    
    cursor.execute('SELECT * FROM UserInfo')
    for row in cursor:
        token_info = {"access token": row.authToken, "refresh token": row.reauthToken,
                      "token expiration": row.tokenExpiration}
        all_users.append(User(row.username, row.mainPlaylistURI, row.backupPlaylistURI,
                              row.songCap, row.minDays, row.lastListenTime, token_info))


# Read the playlist info and store the tracks in a nested dict/json file
def initialize_playlist(user_obj):
    
    playlist = get_playlist_tracks(user_obj)
    for track in playlist:
        track_id = track['track']['id']
        name = track['track']['name']
        artist = track['track']['artists'][0]['name']
        album = track['track']['album']['name']
        listen_count = 0
        
        cursor.execute("INSERT INTO Song (ID, title, artist, album, dateAdded, listenCount, playlistURI) "
                       "VALUES(?,?,?,?,?,?,?)",
                       track_id, name, artist, album, int(time.time()), listen_count, user_obj.playlist_uri)
    
    print('User: ' + user_obj.username + "\nDatabase populated with songs from main playlist")


# Check for new songs added to playlist
def check_songs(user_obj):
    # Get updated tracklist
    current_playlist = get_playlist_tracks(user_obj)
    cursor.execute("SELECT ID FROM Song WHERE playlistURI = ?", user_obj.playlist_uri)
    stored_track_ids = [row.ID for row in cursor]
    
    # Store a list of track IDs in current playlist
    current_tracks = []
    for track in current_playlist:
        track_id = track['track']['id']
        current_tracks.append(track_id)
        
        # If a track is in the playlist and not in playlist_data then add it
        if track_id not in stored_track_ids:
            name = track['track']['name']
            artist = track['track']['artists'][0]['name']
            album = track['track']['album']['name']
            listen_count = 0
            
            cursor.execute("INSERT INTO Song(ID, title, artist, album, dateAdded, listenCount, playlistURI) "
                           "VALUES(?,?,?,?,?,?)",
                           track_id, name, artist, album, int(time.time()), listen_count, user_obj.playlist_uri)
            
            print('User: ' + user_obj.username + '\tNew track found\n\t' +
                  "Name: " + name + "\n\tArtist: " + artist + line)
            
    user_obj.playlist_track_IDs = current_tracks
    
    # If a track in playlist_data is not in the playlist then remove it
    for track_id in stored_track_ids:
        if track_id not in current_tracks:
            cursor.execute("DELETE FROM Song WHERE ID = ? AND playlistURI = ? ",
                           track_id, user_obj.playlist_uri)


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
    results = sp.current_user_recently_played(limit=25)['items']
    
    # Store the new last listen time
    try:
        new_last_listen = int(dateutil.parser.parse(results[0]['played_at']).timestamp())
    except TypeError:
        print("User: " + user_obj.username + "\tError: Nothing returned for recently played" + line)
        user_obj.last_listen_time = int(time.time())
        return
        
    print("\nOld last listen: " + str(user_obj.last_listen_time) +
          "\nNew last listen: " + str(new_last_listen) + "\n")
    
    for track in results:
        track_last_played = int(dateutil.parser.parse(track['played_at']).timestamp())
        
        # Log the listen if it has not already been counted
        if track_last_played > user_obj.last_listen_time:
            track_id = track['track']['id']

            print(str(track_id) + " played at: " + str(track_last_played))
            
            if track_id in user_obj.playlist_track_IDs:
                cursor.execute("UPDATE Song "
                               "SET listenCount = listenCount + 1 "
                               "WHERE ID = ? AND playlistURI = ?",
                               track_id, user_obj.playlist_uri)
                
                print("Song updated for " + user_obj.username + ":\n\tSong: " + str(track_id))

    # Update the user's last listen time
    cursor.execute("UPDATE UserInfo "
                   "SET lastListenTime = ? "
                   "WHERE username = ?",
                   new_last_listen, user_obj.username)
    
    user_obj.last_listen_time = new_last_listen


# Finds the song that has the lowest listens per day ratio
def find_least_listened(user_obj):
    # Save the least listened song's info
    lowest_ratio = 1000.0
    lowest_track_id = None
    
    for track_id in user_obj.playlist_track_IDs:
        track_data = cursor.execute("SELECT dateAdded, listenCount FROM Song "
                                    "WHERE ID = ? AND playlistURI = ?",
                                    track_id, user_obj.playlist_uri).fetchone()
        date_added = track_data.dateAdded
        listen_count = track_data.listenCount
        
        time_delta = datetime.now(timezone.utc) - date_added
        
        # Don't remove songs if they have been in the playlist for less than specified days
        if time_delta.days > user_obj.min_days:
            listen_ratio = listen_count / float(time_delta.days)
            
            if listen_ratio < lowest_ratio:
                lowest_ratio = listen_ratio
                lowest_track_id = track_id
    return lowest_track_id


# Removes least listened to songs until the playlist is at its cap
def trim_playlist(user_obj):
    while len(user_obj.playlist_track_IDs) > user_obj.song_cap:
        track_id = find_least_listened(user_obj)
        if track_id is None:
            return
        
        track_list = [track_id]
        track = user_obj.playlist_data[track_id]
        
        print('User: ' + user_obj.username + '\tLowest listen song removed\n\t' +
              "Name: " + track.name + "\n\tArtist: " + track.artist)
        
        # Remove the song from the playlist, dict, and database
        sp.user_playlist_remove_all_occurrences_of_tracks(user_obj.username, user_obj.playlist_uri, track_list)
        user_obj.playlist_track_IDs.remove(track_id)
        cursor.execute("DELETE FROM Song "
                       "WHERE ID = ? AND playlistURI = ?",
                       track_id, user_obj.playlist_uri)
        
        # Add the song to a backup playlist
        if user_obj.backup_uri != "None" and user_obj.backup_uri is not None:
            sp.user_playlist_add_tracks(user_obj.username, user_obj.backup_uri, track_list)
            print("Track added to backup playlist")
        
        print(line)


# Main method
# Initialize a new user
if sys.argv[1] == "init":
    target_user = sys.argv[2]
    get_all_users()
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
        get_all_users()
        try:
            # Iterate through all users
            for user in all_users:
                sp = user.get_token()
                
                # Process listens
                try:
                    check_songs(user)
                    check_recently_played(user)
                    trim_playlist(user)
                
                # Fetch a new token when the old one expires
                except spotipy.client.SpotifyException as e:
                    print("Error: " + str(e))
                    continue

            time.sleep(10)
            
        except ConnectionError:
            print("Connection Error: Sleeping for 1 min" + line)
            time.sleep(60)
            continue
