#coding: utf8

from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request, session
from engine.deezer_engine import DeezerEngine
from engine import niceUrl
from model.user import User
from model.playlist import Playlist
from forms.playlist_form import SimpleForm
from forms.new_playlist_form import NewPlaylistForm
from log_configurator import allnightdj_logger as log

#TODO : store user in session in order to replace all user = User().find_user(session['token']) declarations
LOGGER = log.get_logger("allnightdj")
MAIN_TITLE="All Night DJ"
PLAYLIST_TO_PLAY = []

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
        url = deezer.get_authentification()
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
    user = deezer.get_user(code)
    tracklist = user['tracklist']
    url_for_tracks = tracklist + "?access_token=" + user['token']
    session['token'] = user['token']
    session['name'] = user['name']

    return redirect('user')

@app.route('/user')
def user():
    user = User().find_user(session['token'])
    return render_template('user.html', title='User page', user=user )

@app.route('/new-playlist', methods=['GET', 'POST'])
def new_playlist():
    user = User().find_user(session['token'])
    form = NewPlaylistForm()

    if form.validate_on_submit():
        playlist_name = form.new_playlist_name.data
        playlist_name = niceUrl.makeMePretty(playlist_name)
        deezer = DeezerEngine()
        json = deezer.create_playlist(user, playlist_name)
        new_playlist_id = json['id']
        user = User().find_user(session['token'])
        return render_template('new-playlist.html', title='New playlist created', user=user, form=form, id=new_playlist_id, playlist_name=playlist_name, success="Y" )
    else:
        print "Oh No..."

    user = User().find_user(session['token'])
    return render_template('new-playlist.html', title='Create a new playlist', user=user, form=form )


@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    deezer = DeezerEngine()
    user = User().find_user(session['token'])
    playlists = deezer.get_playlists_for_user(user)

    list_of_values = []
    for p in playlists:
        list_of_values.append((p['id'], p['title']))

    form = SimpleForm()
    form.checkboxes.choices = list_of_values

    if form.checkboxes.data and form.validate_on_submit():
        PLAYLIST_TO_PLAY=form.checkboxes.data
        p = Playlist()
        playlists = p.find_playlists_by_ids(PLAYLIST_TO_PLAY)
        playlists_for_json = []
        for p in playlists:
            playlists_for_json.append(p['id'])
            playlists_for_json.append(p['duration'])
        LOGGER.info("Duree de la premiere piste : " + str(playlists[0]['duration'])+ " secondes")
        return render_template("player.html", playlists=playlists_for_json, size=len(playlists))
    else:
        print "ERROR ON VALIDATE ON SUBMT"
        print form.errors

    return render_template('user.html', title=MAIN_TITLE, form=form)

@app.route('/tracklist', methods=['GET'])
def tracklist():
    LOGGER.info("Entering /tracklist")
    pid = request.args.get('pid')
    user = User.find_user(session['token'])

    tracklist = DeezerEngine().get_all_tracks_from_playlist(pid)
    playlist = Playlist().find_playlist_with_id(pid)

    return render_template('user.html', title=MAIN_TITLE, user=user, playlist_title=playlist['title'], tracklist=tracklist)


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
