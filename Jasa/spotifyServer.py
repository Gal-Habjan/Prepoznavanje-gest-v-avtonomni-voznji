import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response
import os
import urllib.parse
import base64
import re
import time
from spotifyServerHelper import genericSpotifyFetch, getPlaybackState
from PIL import Image

#for the ai
import numpy as np
import cv2
from shell_image import edge_detection
import torchvision.transforms as transforms
from ultralytics import YOLO


app = Flask(__name__)
path_to_best = "./best.pt"
model = None


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
    #unused
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
    #loggs the user into the spotify, then redirects to the callback backend page with the AccessToken in the url
    print("logging in")
    scope = 'user-read-private user-read-playback-state user-modify-playback-state'
    params={
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,

    }
    url = f'{auth_url}?{urllib.parse.urlencode(params)}'
    # print("my url:", url)
    return redirect(url)


@app.route("/callback")
def callback():
    #saves the token to session storage, then redirects to the frontend with the same token in the url
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



@app.route("/pause",methods=['POST'])
def pause():
    #pauses the song, returns an error if already paused
    url = 'https://api.spotify.com/v1/me/player/pause'
    sucessMessage="paused the song"
    failMessage="failed to pause the song"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/continuePlaying",methods=['POST'])
def continuePlaying():
    #unpauses the song, returns an error if already playing
    print("continuing")
    url = 'https://api.spotify.com/v1/me/player/play'
    sucessMessage="continued playing"
    failMessage="failed to continue playing"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/nextSong",methods=['POST'])
def nextSong():
    #goes to the prev song in queue
    print("next song")
    url = 'https://api.spotify.com/v1/me/player/next'
    sucessMessage="rewound to next song"
    failMessage="failed to go to the next song"
    return genericSpotifyFetch(url, method="POST", sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/previousSong",methods=['POST'])
def previousSong():
    #goes to the prev song in queue
    print("previous song")
    url = 'https://api.spotify.com/v1/me/player/previous'
    sucessMessage="rewound to previous song"
    failMessage="failed to go to previous song"
    return genericSpotifyFetch(url,method="POST", sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/volumeUp",methods=['POST'])
def volumeUp():
    #increases volume by 10, returns the sucess/fail message and code
    print("volume up")
    playback = getPlaybackState()
    volumePercent = -1
    if(playback.status_code < 300):
        volumeData = playback.json()
        print(volumeData)
        volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :",volumePercent)



    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent='+str(min(100,volumePercent+10))
    sucessMessage="increased volume"
    failMessage="failed failed to increase volume"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)

@app.route("/volumeDown",methods=['POST'])
def volumeDown():
    #decreases volume by 10, returns the sucess/fail message and code
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


@app.route("/getState",methods=['POST'])
def getState():
    #returns a json document containing the state of the spotify account

    print("getting state")
    playback = getPlaybackState()
    # print(playback)
    print("returning state")
    return playback


@app.route('/uploadImage', methods=['POST'])
def upload_image():
    # print("started upload----------------")
    data = request.json
    image_data_url = data.get('image')
    try:
        # print("started upload2")
        base64_str = re.search(r'base64,(.*)', image_data_url).group(1)
        image_data = base64.b64decode(base64_str)
        imageArray = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(imageArray, cv2.IMREAD_COLOR)
        # print("arr shape " , imageArray.shape)

        # if image is not None:
        #     print("Array shape:", image.shape)
        # else:
        #     print("Failed to decode image")


        # with open('./uploaded_image.png', 'wb') as f:
        #     f.write(image_data)


        # print("starting image processing ")
        try:
            sign = processImage(image)
        except Exception as err:
            print("error as ", err)
        if(sign is None):
            sign = "no gesture"
        # print("Image successfully uploaded with sign", sign)
        #todo return image containing box
        return Response('{"body": "Image uploaded successfully","sign":"' + sign +'"}', status=200, mimetype='application/json')

    except :
        print("Error during upload:")
        return Response('{"message": "Failed to upload image"}', status=400, mimetype='application/json')
    

def processImage(image):
    image = Image.fromarray(image)
    # print("shape",image.shape)

    # print("tensoreding the image", image.shape, " " , type(image))
    to_tensor = transforms.Compose([
        transforms.ToTensor()
    ])
    # print("got the to_tensor")
    input = to_tensor(image)
    # print("tensored the image")
    input = input.unsqueeze(0)
    # print("unsqueezed the image")
    try:
        # print("getting results")
        results = model(input, verbose=False)
        # print("printing results")
    except Exception as err:
        print("error ", err)
    # print("got results" , results)
    probs = []

    for result in results:
        # result.save(filename='result1.jpg')#todo why does this save to result.jpg, even when the name is different
        boxes = result.boxes  # Boxes object for bounding box outputs
        # print("getting result" , result.names)
        # print("got boxes" , result[0])
        xyxys = boxes.conf
        # print("box", boxes)
        # print("xyxy " , xyxys, boxes.cls[0])
        if(len(boxes.cls) > 0):
            # print("boxes", boxes.cls[0].item())
            # print("names", result.names[int(boxes.cls[0].item())])
            val =  result.names[int(boxes.cls[0].item())]
            print("val \033[94m" + val + '\033[0m')
            return val


    return None

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
    model = YOLO(path_to_best)   
    app.run(host="0.0.0.0", debug=True)

    