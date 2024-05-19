import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,session, make_response, Response

def checkToken(request):
    print("checking token")
    body = request.get_json()
    token = ""
    if "token" in body and "accessToken" not in session:
        session['accessToken'] = body["token"]
        print("using posted token",token)
    if("accessToken" in session):
        token = session['accessToken']
        print("using session token",token)
        return token
    else:
        return None
