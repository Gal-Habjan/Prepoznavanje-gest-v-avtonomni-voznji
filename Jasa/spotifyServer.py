import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response
import os
import urllib.parse
import base64
import re


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
    # if "access_token" not in session:
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

login()
def getAccessTokenFromUrl():
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

    return redirect("http://localhost:3000/?code="+session["access_token"])

@app.route("/pause")
def pause():
    # if "access_token" not in session:
    #     return Response("{'message':'no access token'}", status=400, mimetype='application/json',)
    url = 'https://api.spotify.com/v1/me/player/pause'

    token = ""
    if("access_token" in session):
        token = session['access_token']
        
    headers = {
        'Authorization': 'Bearer ' + token

    }
    # print(headers)
    response = requests.put(url, headers=headers)
    print("pause status code:",response.status_code)



    return  Response("{'a':'b'}", status=response.status_code, mimetype='application/json')


@app.route("/continuePlaying")
def continuePlaying():
    print("continuing")
    url = 'https://api.spotify.com/v1/me/player/play'
    headers = {
        'Authorization': 'Bearer ' + session['access_token'],
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)
    print("continue status code",response.status_code)


    return Response("{'a':'b'}", status=201, mimetype='application/json')
@app.route("/nextSong")
def nextSong():
    print("next song")
    url = 'https://api.spotify.com/v1/me/player/next'
    headers = {
        'Authorization': 'Bearer ' + session['access_token']

    }

    response = requests.post(url, headers=headers)
    print(response)


    return redirect("/")


@app.route("/previousSong")
def previousSong():
    print("previous song")
    url = 'https://api.spotify.com/v1/me/player/previous'
    headers = {
        'Authorization': 'Bearer ' + session['access_token']

    }

    response = requests.post(url, headers=headers)
    print(response)


    return redirect("/")


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
    headers = {
        'Authorization': 'Bearer ' + session['access_token']

    }

    response = requests.put(url, headers=headers)
    print(response)


    return redirect("/")

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
    headers = {
        'Authorization': 'Bearer ' + session['access_token']

    }

    response = requests.put(url, headers=headers)
    print(response)


    return redirect("/")
def getPlaybackState():
    print("getting playback")
    url = 'https://api.spotify.com/v1/me/player'
    headers = {
        'Authorization': 'Bearer ' + session['access_token']

    }

    response = requests.get(url, headers=headers)
    return response

@app.route("/test")
def test():
    print("/test running")
    response = jsonify({"message": "Hello from Flask!"})
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
    #https://accounts.spotify.com/authorize?response_type=code&client_id=f1a15dd2014f41b789ff3cc5ac81ca76&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&scope=user-read-private+user-read-email+user-read-playback-state+user-modify-playback-state
    #https://accounts.spotify.com/authorize?response_type=code&client_id=f1a15dd2014f41b789ff3cc5ac81ca76&redirect_uri=http%3A%2F%2Flocalhost%3A3000&scope=user-read-private%20user-read-email%20user-read-playback-state%20user-modify-playback-state
    return redirect(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    