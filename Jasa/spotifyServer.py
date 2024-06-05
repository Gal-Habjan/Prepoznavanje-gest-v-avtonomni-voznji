import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response
import os
import urllib.parse
import base64
import re
import time
from spotifyServerHelper import genericSpotifyFetch, getPlaybackState
from PIL import Image
import logging

#for the ai
import numpy as np
import cv2
from shell_image import edge_detection
import torchvision.transforms as transforms
from ultralytics import YOLO

from prometheus_client import Counter, generate_latest, REGISTRY, start_http_server

prom_fist = Counter('prom_fist', 'Number of fists detected')
prom_peace = Counter('prom_peace', 'Number of peace signs detected')
prom_thumbsUp = Counter('prom_thumbsUp', 'Number of thumbs up detected')
prom_hand = Counter('prom_hand', 'Number of hands detected')
prom_empty = Counter('prom_empty', 'Number of images without gestures')
prom_error = Counter('prom_error', 'Number of errors')


app = Flask(__name__)
path_to_best = "./Jasa/best.pt"
model = None

@app.route('/metrics')
def metrics():
    print("getting metrics data")
    return generate_latest(REGISTRY), 200

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
    print("getting index data")

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

    return redirect("http://localhost:3001/?code="+session["accessToken"])



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
    if(playback is None):
        return Response('{"message":"cannot access device"}', status=403, mimetype='application/json') 
    volumePercent = -1
    # print(playback)
    volumeData = playback
    # print(volumeData)
    try:
        volumePercent = volumeData["device"]["volume_percent"]
    except:
        print("cannot parse volume data " , volumeData)
        exit(0)
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
    if(playback is None):
        return Response('{"message":"cannot access device"}', status=403, mimetype='application/json') 
    volumePercent = -1
    # print(playback)
    volumeData = playback
    volumePercent = volumeData["device"]["volume_percent"]
    print("got volume :",volumePercent)

    url = 'https://api.spotify.com/v1/me/player/volume?volume_percent='+str(max(0,volumePercent-10))
    sucessMessage="lowered volume"
    failMessage="failed to lower volume"
    return genericSpotifyFetch(url, sucessMessage=sucessMessage , failMessage=failMessage)


@app.route("/getState",methods=['POST'])
def getState():
    #returns a json document containing the state of the spotify account

    # print("getting state")
    playback = getPlaybackState()
    if(playback is None):
        return
    # print(playback)
    # print("returning state")
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
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
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
        prom_error.inc(1)
        return Response('{"message": "Failed to upload image"}', status=400, mimetype='application/json')
    
# imageCounter = 0
def processImage(image):
    # global imageCounter
    # imageCounter += 1

    image = Image.fromarray(image)
    # filename = 'input' + str(imageCounter) + '.jpg'
    # image.save("aaaa.jpg")
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
        # filename = 'result' + str(imageCounter) + '.jpg'
        # result.save(filename)
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
            match val:
                case "fist":
                    logging.debug("prom_fist: %s", prom_fist)
                    prom_fist.inc(1)
                    print("increasing fist counter", prom_fist)
                case "hand":
                    prom_hand.inc(1)
                    print("increasing hand counter")
                case "peace":
                    prom_peace.inc(1)
                    print("increasing peace counter")
                case "thumbs up":
                    prom_thumbsUp.inc(1)
                    print("increasing thumbs counter")
                case "none":
                    prom_empty.inc(1)
                    print("increasing empty counter")
                    
            return val


    prom_empty.inc(1)
    return None

@app.route('/uploadSound',methods=["POST"])
def uploadSound():
    print("UPLOADING SOUND")
    if 'file' not in request.files:
        print("bad request no file")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        print("bad request no file2")
        return jsonify({'error': 'No selected file'}), 400

    if file:
        print("saving to " , file.filename)
        file.save(file.filename)
        return jsonify({'message': 'File uploaded successfully', 'file': file.filename}), 200

    return jsonify({'error': 'File not uploaded'}), 400


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

    