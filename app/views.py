from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request, session
from engine.deezer_engine import DeezerEngine
from engine.db_engine import findUser
from model.user import User
from model.playlist import Playlist
from log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj")
MAIN_TITLE="All Night DJ"

@app.route('/')
def index():
    if 'token' not in session:
        return render_template('index.html', title=MAIN_TITLE)
    else:
        LOGGER.debug("ACCESS TOKEN : " + session['token'])
        LOGGER.debug("User already logged in redirecting to User page ")
        return redirect('/user', code=302)

@app.route('/login')
def login():
    LOGGER.info("Entering Login")

    deezer = DeezerEngine()

    if 'token' not in session:
        url = deezer.getAuthentification()
        LOGGER.debug("URL from Authentification : " + url)

    else:
        LOGGER.debug("ACCESS TOKEN : " + session['token'])
        return redirect('/user', code=302)

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
def playlists():
    deezer = DeezerEngine()
    user = findUser(session['token'])
    playlists = deezer.getPlaylistsForUser(user)

    return render_template('user.html', title=MAIN_TITLE, user=user, playlists=playlists)

@app.route('/tracklist', methods=['GET'])
def tracklist():
    LOGGER.info("Entering /tracklist")
    pid = request.args.get('pid')
    deezer = DeezerEngine()
    pl = Playlist()
    user = findUser(session['token'])
    tracklist = deezer.get_all_tracks_from_playlist(pid)
    playlist = pl.find_playlist_with_id(pid)

    return render_template('tracks.html', title=MAIN_TITLE, user=user, tracklist=tracklist)
    # return redirect('user')

@app.route('/logout')
def logout():
    # TODO : add logout from Deezer API
    if 'token' in session:
        user = User()
        playlist = Playlist()
        deezer = DeezerEngine()
        deezer.logout(session['token'])
        user.remove_user(session['token'])
        playlist.remove_playlists()
        session.clear()
    return render_template('index.html', title=MAIN_TITLE)
