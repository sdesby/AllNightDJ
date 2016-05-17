from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request
from engine.deezer_engine import DeezerEngine
from model.user import User
from log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj")

@app.route('/')
def index():
    return render_template('index.html', title='Super titre de la mort')

@app.route('/login')
def login():
    LOGGER.info("Je suis dans la fonction LOGIN")
    access_token = request.args.get('access_token')
    deezer = DeezerEngine()

    if access_token is None:
        LOGGER.debug("ACCESS TOKEN IS NONE")
        url = deezer.getAuthentification()
        LOGGER.debug("URL from Authentification : " + url)
        print "request endpoint : " + request.endpoint
        if request.endpoint != 'callback':
            LOGGER.debug("Je redirige vers l'url : " + url)
            return redirect(url, code=302)
        else:
            return render_template('index.html', title='Super titre de la mort')
    else:
        LOGGER.debug("ACCESS TOKEN : " + access_token)
        return render_template('index.html', title='Super titre de la mort')

@app.route('/callback')
def deezer_callback():
    LOGGER.info("Entering callback")
    deezer = DeezerEngine()
    code = request.args.get('code')
    user = deezer.getAccessToken(code)
    tracklist = user['tracklist']
    url_for_tracks = tracklist + "?access_token=" + user['token']
    return render_template('user.html', title='User page', user=user, tracklist=url_for_tracks)
