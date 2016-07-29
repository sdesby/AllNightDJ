#coding: utf8

from app import app
from urllib2 import Request
from urlparse import urlparse
from flask import render_template, redirect, request, session, url_for
from engine.deezer_engine import DeezerEngine
from engine import niceUrl
from model.user import User
from model.Deezer.deezer_user import DeezerUser
from model.Deezer.playlist import Playlist
from forms.new_playlist_form import NewPlaylistForm
from forms.signin_form import SignInForm
from forms.fusion_form import FusionForm
from forms.playlist_form import SimpleForm
from forms.login_form import LoginForm
from log_configurator import allnightdj_logger as log

#TODO : store user in session in order to replace all user = DeezerUser().find_user(session['token']) declarations
LOGGER = log.get_logger("allnightdj")
MAIN_TITLE="All Night DJ"
PLAYLIST_TO_PLAY = []

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SignInForm()

    if 'userId' not in session:
        if form.validate_on_submit():
            new_user_name = form.new_user_name.data
            new_user_mail = form.new_user_mail.data
            new_user_password = form.new_user_password.data
            if User().already_exists(new_user_name, new_user_password):
                LOGGER.debug("User \"" + new_user_name + "\" already exists")
                error = unicode("Cet utiliateur existe deja, veuillez vous connecter avec votre compte ou choisir de nouveaux identifiants")
                return render_template('index.html', title=MAIN_TITLE, form=form, error=error)
            else:
                user = User().create_new_user(new_user_name, new_user_mail, new_user_password)
                session['userId'] = user['id']
                print "******* Session user id : " + str(session['userId'])
                return render_template('user.html', title=MAIN_TITLE)
        else:
            return render_template('index.html', title=MAIN_TITLE, form=SignInForm())
    else:
        return render_template('user.html', title=MAIN_TITLE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    LOGGER.info("Entering Login")

    form = LoginForm()

    if form.validate_on_submit():
        user_name = form.user_name.data
        user_password = form.user_password.data

        if User().already_exists(user_name, user_password):
            user = User().find_one_user(user_name, user_password)
            session['userId'] = user['id']
            print "******* Session user id : " + str(session['userId'])
            return render_template('user.html', title=MAIN_TITLE)

        else:
            error = unicode("Unknow user, please retry")
            return render_template('index.html', title=MAIN_TITLE, form=SignInForm(), error=error)

    else:
        return render_template('login.html', title=MAIN_TITLE, form=LoginForm())

@app.route('/callback')
def deezer_callback():
    LOGGER.info("Entering callback")
    deezer = DeezerEngine()
    code = request.args.get('code')
    deezer_user = deezer.get_user(code)
    deezer_user.store_applicationId(session['userId'])
    tracklist = deezer_user['tracklist']
    session['token'] = deezer_user['token']

    return redirect('deezer-user')

@app.route('/deezer-user')
def deezer_user():
    deezer = DeezerEngine()

    if 'token' not in session:
        if request.endpoint != 'callback':
            url = deezer.get_authentification()
            LOGGER.debug("Redirecting to : " + url)
            return redirect(url, code=302)

    else:
        deezer_user = DeezerUser().find_user(session['token'])
        LOGGER.debug("ACCESS TOKEN : " + session['token'])
        return render_template('deezer-user.html', title='User page', user=deezer_user )

@app.route('/new-playlist', methods=['GET', 'POST'])
def new_playlist():
    user = DeezerUser().find_user(session['token'])
    form = NewPlaylistForm()

    if form.validate_on_submit():
        playlist_name = form.new_playlist_name.data
        playlist_name = niceUrl.makeMePretty(playlist_name)
        deezer = DeezerEngine()
        json = deezer.create_playlist(user, playlist_name)
        new_playlist_id = json['id']
        user = DeezerUser().find_user(session['token'])
        return render_template('new-playlist.html', title='New playlist created', user=user, form=form, id=new_playlist_id, playlist_name=playlist_name, success="Y" )

    user = DeezerUser().find_user(session['token'])
    return render_template('new-playlist.html', title='Create a new playlist', user=user, form=form )


@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    deezer = DeezerEngine()
    user = DeezerUser().find_user(session['token'])
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

        if 'play' in request.form:
            playlists_for_json = []
            for p in playlists:
                playlists_for_json.append(p['id'])
                playlists_for_json.append(p['duration'])
            LOGGER.info("Duree de la premiere piste : " + str(playlists[0]['duration'])+ " secondes")
            return render_template("player.html", playlists=playlists_for_json, size=len(playlists))

        elif 'fusion' in request.form:
            LOGGER.info("Request for a fusion")
            fusion_form = FusionForm()
            playlists_ids = []
            for p in playlists:
                playlists_ids.append(p['id'])
            playlists=""
            for ids in playlists_ids:
                playlists += str(ids) + '/'
            return redirect(url_for('playlistsFusion', playlists=playlists, form=fusion_form))

    elif form.is_submitted and not form.checkboxes.data:
        error = unicode("Veuillez choisir au moins une playlist a fusioner")
        return render_template('deezer-user.html', title=MAIN_TITLE, form=form, error=error)

@app.route('/playlists-fusion',  methods=['GET', 'POST'])
def playlistsFusion():
    print "Entering playlist fusion"
    form = FusionForm()
    playlist_ids =request.args.get('playlists')

    if form.validate_on_submit():
        code = form.playlist_code.data
        LOGGER.info(u'Destination playlist Id : ' + code)

        ids_tbl = playlist_ids.split('/')
        ids_tbl.pop()

        tracklists = []
        user = DeezerUser().find_user(session['token'])
        for i in ids_tbl:
            tracklists.append(DeezerEngine().get_track_ids_for_playlist(i, user['token']))

        DeezerEngine().add_tracks_playlist(user, tracklists, code)

    else:
        LOGGER.error("Error validating PlaylistFusion form : ")
        LOGGER.error(form.errors)

    return render_template("playlists-fusion.html", playlists=playlist_ids, form=form)

@app.route('/tracklist', methods=['GET'])
def tracklist():
    LOGGER.info("Entering /tracklist")
    pid = request.args.get('pid')
    user = User.find_user(session['token'])

    tracklist = DeezerEngine().get_all_tracks_from_playlist(pid)
    playlist = Playlist().find_playlist_with_id(pid)

    return render_template('deezer-user.html', title=MAIN_TITLE, user=user, playlist_title=playlist['title'], tracklist=tracklist)


@app.route('/logout')
def logout():
    # TODO : add logout from Deezer API
    if 'token' in session:
        deezer_user = DeezerUser()
        playlist = Playlist()
        deezer = DeezerEngine()
        deezer.logout(session['token'])
        deezer_user.remove_user(session['token'])
        playlist.remove_playlists()
        session.clear()
    return render_template('index.html', title=MAIN_TITLE, form=SignInForm())
