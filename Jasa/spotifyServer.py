import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response
import os
import urllib.parse
import base64
import re
import threading
import webbrowser
import time
import spotifyServerHelper as helper


app = Flask(__name__)
if not app.secret_key:
    app.secret_key = os.urandom(24)
client_id = 'f1a15dd2014f41b789ff3cc5ac81ca76'
client_secret = '1d903db39bd5475fa8540e03b0df7735'
redirect_uri = 'http://localhost:5000/callback'
# redirect_uri = 'http://localhost:3000'

auth_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/'

scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state'  # Add necessary scopes here
@app.route("/")
def index():
    print("got a call")
    # if "accessToken" not in session:
    #     return(redirect("/login"))
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
    params={
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,

    }
    url = f'{auth_url}?{urllib.parse.urlencode(params)}'
    # print("my url:", url)
    return redirect(url)


# def getAccessTokenFromUrl():
#   
#     if "code" in request.args:
#             params = {
#                 'code': request.args['code'],
#                 'grant_type': 'authorization_code',
#                 'redirect_uri': redirect_uri,
#                 'client_id': client_id,
#                 'client_secret': client_secret
#             }
#             response = requests.post(token_url, data=params)
#             print(response.status_code)
#             token_info = response.json()
#             session['accessToken'] = token_info['accessToken']
@app.route("/callback")
def callback():
    print("callbacking")
    if "error" in request.args:
        return Response(('{"message":"'+request["error"] + '"}'), status=400, mimetype='application/json')
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
        session['accessToken'] = token_info['access_token']
        print(session['accessToken'])

    return redirect("http://localhost:3000/?code="+session["accessToken"])

def genericSpotifyFetch(spotifyApiUrl,spotifyApiHeaders= None, sucessMessage = "suceeded", failMessage = "failed"):
    token = helper.checkToken(request)
    if token is None:
        print("log in before pause")
        return Response('{"message":"login to spotify"}', status=403, mimetype='application/json') 
    url = spotifyApiUrl
    headers = ""
    if(spotifyApiHeaders is not None):
        headers = spotifyApiHeaders
    else:
        headers = {
            'Authorization': 'Bearer ' + token

        }

    try:
        response = requests.put(url, headers=headers)
    except:
        return Response('{"message":"'+failMessage+'"}', status=400, mimetype='application/json')
    print("paused music ", response.status_code)
    code = response.status_code
    if(code == 204):
        code = 200

    return Response('{"message":"' +sucessMessage+'"}', status=code, mimetype='application/json') 

@app.route("/pause",methods=['POST'])
def pause():
    url = 'https://api.spotify.com/v1/me/player/pause'
    sucessMessage="paused the song"
    failMessage="failed to pause the song"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/continuePlaying",methods=['POST'])
def continuePlaying():
    print("continuing")
    url = 'https://api.spotify.com/v1/me/player/play'
    sucessMessage="continued playing"
    failMessage="failed to continue playing"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/nextSong")
def nextSong():
    print("next song")
    url = 'https://api.spotify.com/v1/me/player/next'
    sucessMessage="rewound to next song"
    failMessage="failed to go to the next song"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/previousSong")
def previousSong():
    print("previous song")
    url = 'https://api.spotify.com/v1/me/player/previous'
    sucessMessage="rewound to previous song"
    failMessage="failed to go to previous song"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)



@app.route("/volumeUp")
def volumeUp():
    print("volume up")

    playback = getPlaybackState()
    volumePercent = -1
    if(playback.status_code < 300):
        volumeData = playback.json()
        volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :",volumePercent)



    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent='+str(min(100,volumePercent+10))
    sucessMessage="increased volume"
    failMessage="failed failed to increase volume"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/volumeDown")
def volumeDown():
    print("volumeDown")

    playback = getPlaybackState()
    volumePercent = -1
    if(playback.status_code < 300):
        volumeData = playback.json()
        volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :",volumePercent)

    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent='+str(max(0,volumePercent-10))
    sucessMessage="lowered volume"
    failMessage="failed to lower volume"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

def getPlaybackState():
    token = helper.checkToken(request)
    print("getting playback")
    url = 'https://api.spotify.com/v1/me/player'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(url, headers=headers)
    return response



@app.route('/uploadImage', methods=['POST'])
def upload_image():
    print("started upload")
    data = request.json
    image_data_url = data.get('image')
    try:
        print("started upload2")
        base64_str = re.search(r'base64,(.*)', image_data_url).group(1)
        image_data = base64.b64decode(base64_str)


        with open('uploaded_image.png', 'wb') as f:
            f.write(image_data)

        print("Image successfully uploaded")
        return jsonify({'message': 'Image uploaded successfully'}), 200
    except :
        print("Error during upload:")
        return jsonify({'error': 'Failed to upload image'}), 500
    # except(e):
    #     return jsonify({"message": "failed upload" + e})

    return jsonify({"message": "sucesfull upload"})

@app.route("/loginReact")
def loginReact():
    print("logging in")
    scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state'
    params={
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,

    }
    url = f'{auth_url}?{urllib.parse.urlencode(params)}'
    print("my url:", url)
    return redirect(url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    