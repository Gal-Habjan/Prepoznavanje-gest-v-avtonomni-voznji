import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response

def checkToken():
    print("checking token")
    body = request.get_json()
    token = ""
    if "token" in body and "accessToken" not in session:
        session['accessToken'] = body["token"]
        # print("using posted token",token)
    if("accessToken" in session):
        token = session['accessToken']
        # print("using session token",token)
        return token
    else:
        return None


def genericSpotifyFetch(spotifyApiUrl, method = "PUT",spotifyApiHeaders= None, sucessMessage = "suceeded", failMessage = "failed"):
    token = checkToken()
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

    print("headers " , headers, " url, " , url, " token " , token,type(token),  "\n")
    try:
        if(method == "PUT"):
            response = requests.put(url, headers=headers)
        elif(method == "POST"):
            response = requests.post(url, headers=headers)
    
    except:
        return Response('{"message":"'+failMessage+ ', error"}', status=400, mimetype='application/json')
    print(sucessMessage, response.status_code)
    code = response.status_code
    if(code == 204):
        code = 200

    if(code >= 400):
        return Response('{"message":"' +failMessage+'"}', status=code, mimetype='application/json') 
    else:
        return Response('{"message":"' +sucessMessage+'"}', status=code, mimetype='application/json') 
    
def getPlaybackState():
    token = checkToken()
    if token is None:
        print("log in before pause")
        return Response('{"message":"login to spotify"}', status=403, mimetype='application/json') 
    print("getting playback")
    url = 'https://api.spotify.com/v1/me/player'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(url, headers=headers)
    if(response.status_code == 204):
        print("ERROR no device connected")
    


    return response.json()