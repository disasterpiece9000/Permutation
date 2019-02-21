import time
import os
import sys
import spotipy
import spotipy.util as util
from tinydb import TinyDB, Query
from tinydb.operations import increment
from user import User
from track import Track
import dateutil.parser
from datetime import datetime, date, timezone
from requests.exceptions import ConnectionError


# Getting things ready
find_stuff = Query()        # Initiate TinyDB Querry
sp = None                   # Create a gloabal variable for authorized Spotipy
all_users = []              # List of all User objects
path = "./users"            # Path to users folder
folders = os.listdir(path)  # List of all user's folders

# Create all User objects and store in all_users
made_users = False
while made_users == False:
	try:
		for username in folders:
			all_users.append(User(username))
			made_users = True
	except ConnectionError:
		print("Connection Error: Sleeping for 1 min")
		time.sleep(60)
		continue

# Read the playlist info and store the tracks in a nested dict/json file
def initializePlaylist(user):
	user.playlist_data.clear()
	user.playlist_db.purge()

	playlist = getPlaylistTracks(user)
	for track in playlist:
		track_id = track['track']['id']
		date_added = dateutil.parser.parse(track['added_at'])
		name = track['track']['name']
		artist = track['track']['artists'][0]['name']
		album = track['track']['album']['name']
		listen_count = 0

		user.playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
								 'name': name, 'artist': artist, 'album': album,
								'listen_count': listen_count})

		user.playlist_data[track_id] = Track(track_id, date_added, name, artist, album, listen_count)

	print('User: ' + user.username + '\tDatabase generated for playlist\n')

# Check for new songs added to playlist
def checkSongs(user):
	# Get updated tracklist
	current_playlist = getPlaylistTracks(user)

	# Store a list of track IDs in current playlist
	current_tracks = []

	for track in current_playlist:
		track_id = track['track']['id']
		current_tracks.append(track_id)

		# If a track is in the playlist and not in playlist_data then add it
		if track_id not in user.playlist_data:
			date_added = dateutil.parser.parse(track['added_at'])
			name = track['track']['name']
			artist = track['track']['artists'][0]['name']
			album = track['track']['album']['name']
			listen_count = 0

			user.playlist_db.insert({'track_id': track_id, 'date_added': date_added.__str__(),
									 'name': name, 'artist': artist, 'album': album,
									'listen_count': listen_count})

			user.playlist_data[track_id] = Track(track_id, date_added, name, artist, album, listen_count)

			print('User: ' + user.username + '\tNew track: ' + name + ' found in playlist')

	# If a track in playlist_data is not in the playlist then remove it
	for track_id in list(user.playlist_data):
		if track_id not in current_tracks:
			name = user.playlist_data[track_id].name
			del user.playlist_data[track_id]
			user.playlist_db.remove(find_stuff.track_id == track_id)

			print('User: ' + user.username + '\tRemoved track from playlist: ' + name)


# Gets paginated results from playlist track list
def getPlaylistTracks(user):
	results = sp.user_playlist_tracks(user.username, user.playlist_uri)
	tracks_dict = results['items']

	while results['next']:
		results = sp.next(results)
		tracks_dict.extend(results['items'])

	return tracks_dict

# Get recently played songs and log them
def checkRecentlyPlayed(user):
	results = sp.current_user_recently_played(limit=25)

	# Store the new last listen time
	try:
		new_last_listen = dateutil.parser.parse(results['items'][0]['played_at'])
	except TypeError:
		print("User: " + user.username + "\tError: Nothing returned for recently played")
		new_last_listen = user.last_listen_time

	for track in results['items']:
		track_last_played = dateutil.parser.parse(track['played_at'])

		# Log the song if it has not already been counted
		if track_last_played > user.last_listen_time:
			track_id = track['track']['id']
			if track_id in user.playlist_data:
				logListen(user, track)
	# Return the time of the most recently processed song
	return new_last_listen

# Log songs listened to
def logListen(user, track_dict):
	track_id = track_dict['track']['id']
	track = user.playlist_data[track_id]

	# Increment listen count
	track.listen_count += 1
	user.playlist_db.update({'listen_count': track.listen_count}, find_stuff.track_id == track_id)

	print('User: ' + user.username + '\tTrack: ' + track.name + ' listen count incremented to ' + str(track.listen_count))

# Finds the song that has the lowest listens per day ratio
def findLeastListened(user):
	# Save the least listened song's info
	lowest_ratio = 1000.0
	lowest_track_id = None

	for track_id in user.playlist_data:
		track = user.playlist_data[track_id]
		time_delta = datetime.now(timezone.utc) - track.date_added

		# Don't remove songs if they have been in the playlist for less than 2 weeks
		if time_delta.days > user.min_days:
			listen_ratio = track.listen_count / float(time_delta.days)

			if listen_ratio < lowest_ratio:
				lowest_ratio = listen_ratio
				lowest_track_id = track.id
	return lowest_track_id

# Removes least listened to songs until the playlist is at its cap
def trimPlaylist(user):
	while len(user.playlist_data) > user.song_cap:
		track_id = findLeastListened(user)
		if track_id == None:
			return
		track = []
		track.append(track_id)

		print('User: ' + user.username + '\tRemoved track from playlist: ' + user.playlist_data[track_id].name)

		# Remove the song from the playlist, dict, and database
		sp.user_playlist_remove_all_occurrences_of_tracks(user.username, user.playlist_uri, track)
		del user.playlist_data[track_id]
		user.playlist_db.remove(find_stuff.track_id == track_id)

		# Add the song to a backup playlist
		if user.backup_uri != "None" and user.backup_uri != None:
			sp.user_playlist_add_tracks(user.username, user.backup_uri, track)
			print("User: " + user.username + "\tTrack added to secondary playlist")


# Main method
# Initalize a new user
if sys.argv[1] == "init":
	target_user = sys.argv[2]
	for user in all_users:
		# If the user has been created, initialize the playlist data
		if user.username.lower() == target_user.lower():
			sp = user.getToken()
			initializePlaylist(user)
			print(user.username + " was initialized\nExiting now...")
			sys.exit(0)

	print("User: " + user.username + "\tThat user was not found. Please make sure they have a folder and .ini file")
	sys.exit(0)

# Run continuously through all users
elif sys.argv[1] == "auto":
	while(True):
		try:
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
					sp = user.getToken()
					continue
		except ConnectionError:
			print("Connection Error: Sleeping for 1 min")
			time.sleep(60)
			continue
