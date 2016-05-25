from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request, session
from engine.deezer_engine import DeezerEngine
from engine.db_engine import findUser
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
    user = findUser(session['token'])
    return render_template('user.html', title='User page', user=user )

@app.route('/playlists')
def tracklist():
    deezer = DeezerEngine()
    user = findUser(session['token'])
    playlists = deezer.getPlaylistsForUser(user)
    playlist_title= []
    for t in playlists:
        playlist_title.append(t['title'])

    return render_template('user.html', title=MAIN_TITLE, user=user, playlist=playlist_title)

@app.route('/logout')
def logout():
    # TODO : add logout from Deezer API
    # TODO : remove user from Database
    deezer = DeezerEngine()
    deezer.logout(session['token'])
    session.clear()
    return render_template('index.html', title=MAIN_TITLE)
