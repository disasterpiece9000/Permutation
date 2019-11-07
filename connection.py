import base64
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

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=permutation2.c06ndc8a9kh3.us-east-1.rds.amazonaws.com,1433;'
                      'uid=admin;'
                      'pwd=password;'
                      'Database=Permutation;'
                      'Trusted_Connection=no;',
                      autocommit=True)
cursor = conn.cursor()


def database_insert(username, access, playlists):
    cursor.execute("IF NOT EXISTS ("
                   "SELECT username FROM UserInfo "
                   "WHERE username = ?"
                   ") "
                   "BEGIN "
                   "INSERT INTO UserInfo(username, authToken, reauthToken) "
                   "VALUES(?,?,?) "
                   "END",
                   username, username, access['access_token'], access['refresh_token'])
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
        username_url = "https://api.spotify.com/v1/me"


        code = request.form["code"]
        token_info = ""
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':REDIRECT_URI
        }
        auth_header=base64.b64encode(six.text_type(CLIENT_ID+':'+CLIENT_SECRET).encode('ascii'))
        headers = {'Authorization':'Basic %s' % auth_header.decode('ascii')}
        response = requests.post(token_url,data=payload,headers=headers)
        access = literal_eval(response.text)
        access_info = access
        print(json.dumps(access))
        sp = spotipy.Spotify(auth=access["access_token"])
        username_header = {'Authorization':'Bearer %s' % access['access_token']}
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
                print(playlist['name']+" uri:"+playlist['id'])
                if count == 0:
                    playlsts = playlsts + (playlist['name'] + "|" + playlist["images"][0]['url'])
                else:
                    playlsts = playlsts + (";" + playlist['name']+"|"+playlist["images"][0]['url'])
                count = count + 1
        data['playlists'] = playlsts
        t1 = threading.Thread(target=database_insert, args=(username, access, playlists))
        t1.start()
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


if __name__ == '__main__':
    app.run()


