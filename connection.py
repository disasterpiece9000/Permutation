import base64
import time

from flask import Flask, request, render_template
from flask_cors import CORS
import requests
import six
import json
import spotipy
from ast import literal_eval
import pyodbc
import threading

app = Flask(__name__)
app.debug = True
cors = CORS(app, resources={r"/*": {"origins": "*"}})
USERNAME = 'oh_snap272'
CLIENT_ID = '56a50cf4ff574e438f3e1858604a780a'
CLIENT_SECRET = 'decd57a138e64e5c9ff46d742a4428aa'
REDIRECT_URI = 'http://localhost:8080/main.html'
SCOPE = "playlist-modify-private playlist-modify-public user-read-recently-played"
access_info = None
sp = None
selectedPlaylist = None

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=permutation2.c06ndc8a9kh3.us-east-1.rds.amazonaws.com,1433;'
                      'uid=admin;'
                      'pwd=password;'
                      'Database=Permutation;'
                      'Trusted_Connection=no;',
                      autocommit=True)
if conn:
    print("connected")
else:
    print("error")
cursor = conn.cursor()


def database_update(tracks_dict, playlistId):
    for track in tracks_dict:
        track_id = track['track']['id']
        name = track['track']['name']
        artist = track['track']['artists'][0]['name']
        album = track['track']['album']['name']
        listen_count = 0

        cursor.execute("INSERT INTO Song (ID, title, artist, album, dateAdded, listenCount, playlistURI) "
                       "VALUES(?,?,?,?,?,?,?)",
                       track_id, name, artist, album, int(time.time()), listen_count, playlistId)


def database_insert(username, access, playlists):
    print('1')
    cursor.execute("IF NOT EXISTS ("
                   "SELECT username FROM UserInfo "
                   "WHERE username = ?"
                   ") "
                   "BEGIN "
                   "INSERT INTO UserInfo(username, authToken, reauthToken) "
                   "VALUES(?,?,?) "
                   "END",
                   username, username, access['access_token'], access['refresh_token'])
    print('2')
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            print(playlist['name'] + " uri:" + playlist['id'])
            cursor.execute("IF NOT EXISTS ("
                           "SELECT username, URI FROM Playlist "
                           "WHERE username = ? AND URI = ?"
                           ") "
                           "BEGIN "
                           "INSERT INTO Playlist(URI, name, username) "
                           "VALUES(?,?,?) "
                           "END",
                           username, playlist["id"], playlist["id"], playlist["name"], username)
    return


@app.route("/start", methods=['GET' , 'POST'])
def index():
    global USERNAME
    global sp
    global access_info
    if request.method == "POST":
        data = {}
        username = USERNAME
        data['username'] = USERNAME
        playlists = sp.user_playlists(username)
        playlsts = ''
        print("Getting playlists")
        count = 0
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                if count == 0:
                    playlsts = playlsts + (playlist['name'] + "|" + playlist["images"][0]['url'])
                else:
                    playlsts = playlsts + (";" + playlist['name']+"|"+playlist["images"][0]['url'])
                count = count + 1
        data['playlists'] = playlsts

        return json.dumps(data)
    return


@app.route("/refresh", methods=['GET' , 'POST'])
def refresh():
    if request.method == "POST":
        refresh_url = "https://accounts.spotify.com/api/token"  # from the docs

        payload = {
            'refresh_token': access_info['refresh_token'],
            'grant_type': 'refresh_token'
        }

        auth_header = base64.b64encode(six.text_type(CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii'))
        headers = {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

        response = requests.post(refresh_url, data=payload, headers=headers)

        token_info = response.json()
        return json.dumps(token_info)
    return render_template("main.html")


@app.route("/playlists", methods=['GET' , 'POST'])
def get_playlists():
    global sp
    if request.method == "GET":
        sp = spotipy.Spotify(auth=access_info["access_token"])
        playlists = sp.user_playlists(USERNAME)
        playlsts=''
        for playlist in playlists['items']:
            if playlist['owner']['id'] == USERNAME:
                print()
                playlsts = playlsts+(";"+playlist['name'])
                print(playlist['name'])
        return playlsts
    return


@app.route("/confirm", methods=['GET','POST'])
def confirm_selection():
    global selectedPlaylist
    global sp
    if request.method == "POST":
        data = {}
        playlist = request.form["playlist"]
        print(playlist)
        playlists = sp.user_playlists(USERNAME)
        for p in playlists['items']:
            if p['owner']['id'] == USERNAME:
                if p["name"] == playlist:
                    print("selected playlist "+p['name'])
                    results = sp.user_playlist(USERNAME, p['id'], fields="tracks,next")
                    tracks = results['tracks']
                    data['tracks'] = tracks
                    data['playlist'] = p
                    selectedPlaylist = json.dumps(data)
                    print(selectedPlaylist)
                    selectedPlaylist = json.loads(selectedPlaylist)
                    return selectedPlaylist

    if request.method == "GET":
        if selectedPlaylist is not None:
            print('returning '+selectedPlaylist['playlist']['name'])
            return selectedPlaylist


@app.route("/stats", methods=['POST'])
def stats():
    if request.method == 'POST':
        data = request.get_json(force=True)
        username = USERNAME
        cursor.execute("SELECT ID, title, artist, album, dateAdded, listenCount "
                       "FROM UserInfo JOIN Song ON UserInfo.mainPlaylistURI = song.playlistURI "
                       "WHERE username = ?", username)
        return_data = []
        for row in cursor.fetchall():
            return_data.append({"id": row.ID, "title": row.title, "artist": row.artist, "album": row.album,
                                "date added": row.dateAdded, "listen count": row.listenCount})

        return json.dumps({"tracks": return_data})


@app.route("/main", methods=['POST'])
def main_page():
    global USERNAME
    global sp
    global access_info
    if request.method == "POST":
        data = {}
        username_url = "https://api.spotify.com/v1/me"

        if access_info is None:
            code = request.form["code"]
            token_info = ""
            token_url = "https://accounts.spotify.com/api/token"
            payload = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
            auth_header = base64.b64encode(six.text_type(CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii'))
            headers = {'Authorization': 'Basic %s' % auth_header.decode('ascii')}
            response = requests.post(token_url, data=payload, headers=headers)
            access = literal_eval(response.text)
            access_info = access
            print(json.dumps(access))
        sp = spotipy.Spotify(auth=access_info["access_token"])
        username_header = {'Authorization': 'Bearer %s' % access_info['access_token']}
        username_response = requests.get(url=username_url, headers=username_header)
        username_json = json.loads(username_response.text)
        username = username_json['display_name']
        USERNAME = username
        data['username'] = username

        playlists = sp.user_playlists(username)
        playlsts = ''
        print("Getting playlists")
        count = 0
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                if count == 0:
                    playlsts = playlsts + (playlist['name'] + "|" + playlist["images"][0]['url'])
                else:
                    playlsts = playlsts + (";" + playlist['name'] + "|" + playlist["images"][0]['url'])
                count = count + 1
        data['playlists'] = playlsts

        playlistData = {}
        cursor.execute("SELECT * FROM UserInfo WHERE username='"+username+"'")
        backupPlaylist = None
        fetch = cursor.fetchone()
        if fetch.mainPlaylistURI is None:
            return json.dumps(playlistData)
        mainPlaylistId = fetch.mainPlaylistURI
        mainPlaylist = sp.user_playlist(USERNAME, mainPlaylistId)
        if fetch.backupPlaylistURI is not None:
            backupPlaylistId = fetch.backupPlaylistURI
            backupPlaylist = sp.user_playlist(USERNAME, backupPlaylistId)





        #t1 = threading.Thread(target=database_insert, args=(username, access_info, playlists))
        #t1.start()

        playlistData['mainPlaylist'] = mainPlaylist
        if backupPlaylist is not None:
            playlistData['backupPlaylist'] = backupPlaylist
        else:
            playlistData['backupPlaylist'] = 'none'
        cursor.execute("SELECT songCap, minDays FROM UserInfo WHERE username = ?", username)
        data = cursor.fetchone()
        playlistData['songCap'] = data.songCap
        playlistData['gracePeriod'] = data.minDays
        playlistData['username'] = username
        return json.dumps(playlistData)
    return


@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        james = request.get_json(force=True)
        print(james['type'])
        type = james['type']
        name = james['username']
        playlistId = james['playlistId']

        if type == 'main':
            cursor.execute("SELECT mainPlaylistURI FROM UserInfo WHERE username = ?", name)
            current_main_playlist_id = cursor.fetchone().mainPlaylistURI

            cursor.execute("DELETE FROM Song WHERE playlistURI = ?", current_main_playlist_id)
            cursor.execute("UPDATE UserInfo SET mainPlaylistURI = ?", playlistId)

            results = sp.user_playlist_tracks(name, playlistId)
            tracks_dict = results['items']

            while results['next']:
                results = sp.next(results)
                tracks_dict.extend(results['items'])

            #t1 = threading.Thread(target=database_update, args=(tracks_dict, playlistId))
            #t1.start()
            database_update(tracks_dict,playlistId)

        else:
            cursor.execute("UPDATE UserInfo SET backupPlaylistURI = ? WHERE username = ?", playlistId, name)
        return json.dumps({})


@app.route("/settings", methods=['POST'])
def settings():
    if request.method == 'POST':
        james = request.get_json()
        print(str(james))
        song_cap = james['song cap']
        grace_period = james['grace period']
        name = james['user']

        cursor.execute("UPDATE UserInfo SET songCap = ?, minDays = ? WHERE username = ?", song_cap, grace_period, name)
        return json.dumps({})



@app.route("/recommended", methods=['GET'])
def recommend():
    print("sending rocommended")
    if request.method == "GET":
        t = access_info["access_token"]
        results = sp.current_user_top_tracks(limit=5, time_range='short_term')
        tracks_dict = results['items']
        while results['next']:
            results = sp.next(results)
            tracks_dict.extend(results['items'])
        top_list = ""
        count = 0
        test = ""
        for x in tracks_dict:
            if count > 4:
                continue
            if count == 0:
                top_list = top_list + x['id']
            else:
                top_list = top_list+","+x['id']
            count = count+1
        url = "https://api.spotify.com/v1/recommendations?"
        url = url + "seed_tracks="+top_list + "&" + "market=US"
        header = {'Authorization':'Bearer %s' % t}
        response = requests.get(url=url,headers=header)
        r = response.json()
        return json.dumps(r)


if __name__ == '__main__':
    app.run()


