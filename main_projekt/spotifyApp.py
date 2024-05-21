import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import urllib.parse

# class SpotifyApp:
#     def __init__(self):
#         self.app = Flask(__name__)
#         self.app.secret_key = os.urandom(24)
#         self.session = session
#
#     def start(self):
#         self.app.run(host="0.0.0.0")
#

app = Flask(__name__)
if not app.secret_key:
    app.secret_key = os.urandom(24)
access_token = None
client_id = 'b1c9e17669784d0b9d3a8dc21cbd2c89'
client_secret = '2c0e3a4a19f44b3aa83302880f544edb'
redirect_uri = 'http://localhost:5000/callback'

auth_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/'

scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state'  # Add necessary scopes here


@app.route("/")
def index():
    if "access_token" not in session and access_token is None:
        return redirect("/login")
    return ("<div> <a href='/login'>login</a> </div>"
            "<div><a href='/continuePlaying'>continue</a></div>"
            "<div><a href='/pause'>pause</a></div>"
            "<div><a href='/nextSong'>next song</a></div>"
            "<div><a href='/previousSong'>previous song</a></div>"
            "<div><a href='/volumeUp'>volume up</a></div>"
            "<div><a href='/volumeDown'>volume down</a></div>"
            )


@app.route("/login")
def login():
    print("logging in")
    scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state'
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'show_dialog': True,

    }
    # response = requests.post(auth_url, data=params)
    # print(response.status_code)
    url = f'{auth_url}?{urllib.parse.urlencode(params)}'

    return redirect(url)


@app.route("/callback")
def callback():
    print("callbacking")
    if "error" in request.args:
        return jsonify({'error': request.args['error']})
    if "code" in request.args:
        params = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(token_url, data=params)
        print(response.status_code)
        token_info = response.json()
        session['access_token'] = token_info['access_token']

        print(session['access_token'])
        global access_token  # ce je ze global ani
        access_token = session['access_token']

    return redirect("/")


@app.route("/pause")
def pause():
    print("pausing")
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    state = getPlaybackState()

    if state.json()["is_playing"] == True:
        url = 'https://api.spotify.com/v1/me/player/pause'
        headers = {
            'Authorization': 'Bearer ' + token

        }

        response = requests.put(url, headers=headers)
    else:
        url = 'https://api.spotify.com/v1/me/player/play'
        headers = {
            'Authorization': 'Bearer ' + token,
            "Content-Type": "application/json"
        }

        response = requests.put(url, headers=headers)

    print(response)

    return redirect("/")


@app.route("/continuePlaying")
def continuePlaying():
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("continuing")
    url = 'https://api.spotify.com/v1/me/player/play'
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)
    print(response)

    return redirect("/")


@app.route("/nextSong")
def nextSong():
    global access_token
    print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("next song")
    url = 'https://api.spotify.com/v1/me/player/next'
    headers = {
        'Authorization': 'Bearer ' + token

    }

    response = requests.post(url, headers=headers)
    print(response)

    return redirect("/")


@app.route("/previousSong")
def previousSong():
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("previous song")
    url = 'https://api.spotify.com/v1/me/player/previous'
    headers = {
        'Authorization': 'Bearer ' + token

    }

    response = requests.post(url, headers=headers)
    print(response)

    return redirect("/")


@app.route("/volumeUp")
def volumeUp():
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("volume up")

    playback = getPlaybackState()
    volumePercent = -1
    if (playback.status_code < 300):
        volumeData = playback.json()
        volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :", volumePercent)

    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent=' + str(min(100, volumePercent + 10))
    headers = {
        'Authorization': 'Bearer ' + token

    }

    response = requests.put(url, headers=headers)
    print(response)

    return redirect("/")


@app.route("/volumeDown")
def volumeDown():
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("volumeDown")

    playback = getPlaybackState()
    volumePercent = -1
    if (playback.status_code < 300):
        volumeData = playback.json()
        volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :", volumePercent)

    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent=' + str(max(0, volumePercent - 10))
    headers = {
        'Authorization': 'Bearer ' + token

    }

    response = requests.put(url, headers=headers)
    print(response)

    return redirect("/")


@app.route("/get_data")
def get_data():
    print("fuck")
    return session["access_token"]


@app.route('/update', methods=['PUT'])
def update():
    data = request.json
    # Process the data here
    print(data)  # Just print the data for demonstration purposes
    return jsonify({"message": "Data received", "data": data}), 200


def getPlaybackState():
    global access_token
    # print(access_token)
    token = ""
    if "access_token" not in session:
        token = access_token
    else:
        token = session['access_token']
    print("getting playback")
    url = 'https://api.spotify.com/v1/me/player'
    headers = {
        'Authorization': 'Bearer ' + token

    }

    response = requests.get(url, headers=headers)
    return response


def call_toggle_pause():
    url = 'http://127.0.0.1:5000/pause'

    r = requests.get(url)


def call_pause():
    url = 'http://127.0.0.1:5000/pause'

    r = requests.get(url)


def call_continue():
    url = 'http://127.0.0.1:5000/continuePlaying'

    r = requests.get(url)


def call_next_song():
    url = 'http://127.0.0.1:5000/nextSong'

    r = requests.get(url)


def call_volume_up():
    url = 'http://127.0.0.1:5000/volumeUp'

    r = requests.get(url)


def call_volume_down():
    url = 'http://127.0.0.1:5000/volumeDown'

    r = requests.get(url)


if __name__ == "__main__":
    print("main")
    app.run(host="0.0.0.0", port=5000)
