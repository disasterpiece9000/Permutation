# Permutation
### Automating the perfect Spotify playlist

Permutation will automatically remove the least listened to songs in your playlist. Simply select a playlist and a song cap. When you find a new song you like, just add it to the playlist. Permutation will automatically replace your least listened to song with the new one. This ensures that your playlist will always be fresh, while not letting it grow out of control.

___

## Features:
* **Always up to date** - Permutation is always checking what songs you're listening to so it never misses a beat!
* **Song cap** - Set the maximum number of songs you want in the playlist and Permutation will ensure that it never goes over.
* **Grace period** - Permutation can make sure that song you just added has time to settle in before it gets the boot. You can give new additions a grace period where they will be immune from being removed.
* **Discard pile** - Don't let those removed songs disappear into the abyss! Setup a secondary playlist and Permutation will store all the removed songs in it. It's perfect for a trip down memory lane.

## Upcomming Features:
* **Multiple playlist management** - Currently Permutation only supports one playlist per account. In a future update, accounts will be able to maintain an unlimited number of playlists!
* **No cap mode** - If you're not concerned about the size of your playlist, then you will be able confirgure Permutation to only remove songs once they cross below a certain threshold of listens per day.
* **???** - Why do I have to come up with all the ideas? I want to hear what you people want!

____

## Configuration:
Create a file called settings.ini with the following text and fill in the fields:
```
[ACCNT_INFO]
username = 
# URI of the playlist that will be managed by the program
main_playlist = 
# URI of the playlist that the removed songs will be added to
backup_playlist = 

[SETTINGS]
# Maximun number of songs in the main playlist
song_cap = 
# Number of days a song is in the main playlist before it can be removed
min_days = 
```
### What goes where?
* **username** - Your username or your account's URI link
* **main_playlist** - Your main playlist's ID or URI link
* **backup_playlist** - Your secondary playlist's ID or URI link. This can also be set to None to disable.
* **song_cap** - Any number greater than 0
* **min_days** - Any number. This can also be set to 0 to disable.
