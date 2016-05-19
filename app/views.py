from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request, session
from engine.deezer_engine import DeezerEngine
from model.user import User
from log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj")
MAIN_TITLE="All Night DJ"

@app.route('/')
def index():
    #if 'token' in session:

        #return render_template('user.html', title='User page', user=session['user'])
    #else:
    return render_template('index.html', title=MAIN_TITLE)

@app.route('/login')
def login():
    LOGGER.info("Entering Login")
    #access_token = request.args.get('access_token')
    deezer = DeezerEngine()

    #if access_token is None:
    #    LOGGER.debug("Access token is NONE")

    if 'token' not in session:
        url = deezer.getAuthentification()
        LOGGER.debug("URL from Authentification : " + url)

    else:
        LOGGER.debug("ACCESS TOKEN : " + session['token'])
        return render_template('index.html', title=MAIN_TITLE)

    if request.endpoint != 'callback':
        LOGGER.debug("Redirecting to : " + url)
        return redirect(url, code=302)
    else:
        return render_template('index.html', title=MAIN_TITLE)
    #else:
    #    LOGGER.debug("ACCESS TOKEN : " + access_token)
    #    return render_template('index.html', title=MAIN_TITLE)

@app.route('/callback')
def deezer_callback():
    LOGGER.info("Entering callback")
    deezer = DeezerEngine()
    code = request.args.get('code')
    user = deezer.getUser(code)
    tracklist = user['tracklist']
    url_for_tracks = tracklist + "?access_token=" + user['token']
    session['token'] = user['token']

    return redirect('user')

@app.route('/user')
def user():
    print "======= Youhou ! User page !"
    #TODO retrieve user from token to use in user.html
    return render_template('user.html', title='User page')

@app.route('/logout')
def logout():
    # TODO : add logout from Deezer API
    session.clear()
    return render_template('index.html', title=MAIN_TITLE)
