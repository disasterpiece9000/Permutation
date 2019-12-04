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

line = "\n---------------------------------------------------\n"

# Getting things ready
sp = None  # Create a global variable for authorized Spotipy


# Create all User objects and store in all_users
def get_all_users():
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM UserInfo")
    return [row.username for row in cursor.fetchall()]
    
    
def get_user():
    cur = conn.cursor()
    cur.execute('SELECT * FROM UserInfo WHERE username = ?', username)
    row = cur.fetchone()
    token_info = {"access_token": row.authToken, "refresh_token": row.reauthToken,
                  "expires_at": row.tokenExpiration}
    return User(row.username, row.mainPlaylistURI, row.backupPlaylistURI,
                row.songCap, row.minDays, row.lastListenTime, token_info, conn)


# Check for new songs added to playlist
def check_songs(user_obj):
    # Get updated tracklist
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Song WHERE playlistURI = ?", user_obj.playlist_uri)
    stored_track_ids = [row.ID for row in cursor]
    current_playlist = get_playlist_tracks(user_obj)
    
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
            album_img = track['track']['album']['images'][2]['url']
            listen_count = 0
            
            cursor.execute("INSERT INTO Song(ID, title, artist, album, dateAdded, listenCount, playlistURI, albumImg) "
                           "VALUES(?,?,?,?,?,?,?,?)",
                           track_id, name, artist, album, int(time.time()), listen_count,
                           user_obj.playlist_uri, album_img)
            
            print('User: ' + user_obj.username + '\tNew track found\n\t' +
                  "Name: " + name + "\n\tArtist: " + artist + line)
    
    user_obj.playlist_track_IDs = current_tracks
    
    # If a track in playlist_data is not in the playlist then remove it
    for track_id in stored_track_ids:
        if track_id not in current_tracks:
            cursor.execute("DELETE FROM Song WHERE ID = ? AND playlistURI = ? ",
                           track_id, user_obj.playlist_uri)
            
            print('User: ' + user_obj.username + '\nTrack deleted\n\t' +
                  "ID: " + track_id + line)


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
    cursor = conn.cursor()
    results = sp.current_user_recently_played(limit=25)['items']
    
    # Store the new last listen time
    try:
        new_last_listen = int(dateutil.parser.parse(results[0]['played_at']).timestamp())
    except TypeError:
        print("User: " + user_obj.username + "\tError: Nothing returned for recently played" + line)
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
        cursor = conn.cursor()
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
        
        print('User: ' + user_obj.username + '\tLowest listen song removed\n\tID: ' + track_id)
        
        # Remove the song from the playlist, dict, and database
        sp.user_playlist_remove_all_occurrences_of_tracks(user_obj.username, user_obj.playlist_uri, track_list)
        user_obj.playlist_track_IDs.remove(track_id)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Song "
                       "WHERE ID = ? AND playlistURI = ?",
                       track_id, user_obj.playlist_uri)
        
        # Add the song to a backup playlist
        if user_obj.backup_playlist != "None" and user_obj.backup_playlist is not None:
            sp.user_playlist_add_tracks(user_obj.username, user_obj.backup_playlist, track_list)
            print("Track added to backup playlist")
        
        print(line)


# Main method
# Run continuously through all users
while True:
    all_users = get_all_users()
    try:
        # Iterate through all users
        for username in all_users:
            user = get_user()
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
        
        time.sleep(60)
    
    except ConnectionError:
        print("Connection Error: Sleeping for 1 min" + line)
        time.sleep(60)
        continue
