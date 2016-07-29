#coding: utf8

import urllib2 as urllib2
from urllib2 import Request, urlopen, URLError
from urlparse import urlparse
import json
import requests
from ..model.Deezer.deezer_user import DeezerUser
from ..model.Deezer.playlist import Playlist
from ..db import database_init as db
from ..log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("DeezerEngine")
DEEZER_LOGOUT_URL='http://www.deezer.com/logout.php'

class DeezerEngine:

    def __init__(self):
        self.APP_ID = 'app_id=175951'
        self.APP_SECRET = 'secret=faf5d50ee902f4ea448f0d959f126239'
        self.AUTH_URL = 'https://connect.deezer.com/oauth/auth.php'
        self.TOKEN_URL = 'https://connect.deezer.com/oauth/access_token.php'
        self.redirect_uri='redirect_uri=http://127.0.0.1:5000/callback'
        self.permissions = 'perms=basic_access,email, manage_library'
        self.response_type="response_type=token"

    def get_authentification(self):
        LOGGER.info("Entering get_authentification function")
        url = self.AUTH_URL + "?" + self.APP_ID + "&" + self.redirect_uri + "&" + self.permissions

        try:
            LOGGER.debug("Requested url : " + url)
            return url

        except URLError, e:
            LOGGER.error("URLError with remote server :" , e)

    def get_user(self, code):
        LOGGER.info("Entering get_user")
        CODE_FOR_TOKEN = "code=" + code
        url_to_get_token = self.TOKEN_URL + "?" + self.APP_ID + "&" + self.APP_SECRET + "&" + CODE_FOR_TOKEN + "&output=json"
        LOGGER.debug("Requesting url: " + url_to_get_token)
        request = Request(url_to_get_token)
        response = urlopen(request)
        parsed_json = json.load(response)
        access_token = parsed_json["access_token"]

        LOGGER.info("Leaving get_user")
        return self.get_user_with_token(access_token)

    def get_user_with_token(self, token):
        LOGGER.info("Entering get_user_with_token")
        user = DeezerUser()
        already_exists = user.find_user(token)

        if not already_exists:
            url = "http://api.deezer.com/user/me?access_token=" + token
            request = Request(url)

            try:
                LOGGER.debug("Requested url : " + url)
                response = urlopen(request)
                parsed_json = json.loads(response.read())
                LOGGER.debug("Response: ")
                LOGGER.debug(parsed_json)
                LOGGER.info("Leaving get_user_with_token")
                return user.store_user(parsed_json, token)

            except URLError, e:
                LOGGER.error("Error while communicating with remote server :" , e)

        else:
            return user.find_user(token)

    def get_playlists_for_user(self, user):
        LOGGER.info("Entering get_playlists_for_user")
        playlist = Playlist()
        alreadyHasPlaylists = playlist.already_has_playlist()

        if alreadyHasPlaylists:
            playlist.remove_playlists()

        #if not alreadyHasPlaylists:
        url = "http://api.deezer.com/user/me/playlists?access_token=" + user['token']
        request = Request(url)

        try:
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("Response: " + str(parsed_json))

            playlist.storePlaylists(parsed_json)
            return playlist.find_playlists()

        except URLError, e:
            LOGGER.error("Error while communicating with remote server :" , e)
        #else:
        #    return playlist.find_playlists()

    def create_playlist(self, user, playlist_name):
        url = "https://api.deezer.com/user/" + str(user['id']).encode('utf-8') + "/playlists?title=" + playlist_name.encode('utf-8') + "&access_token=" + user['token'].encode('utf-8')
        try:
            request = Request(url, data="")
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
        #    LOGGER.debug("Response: " + str(parsed_json))
            return parsed_json

        except URLError, e:
            LOGGER.error("Error while communicating with remote server : " , e)

    def add_tracks_playlist(self, user, tracklist, pid):
        songs=""
        end = len(tracklist)-1;
        for i in range(end+1):
            for j in tracklist[i]:
                songs +=str(j)+','

        songs=songs[:-1]
        LOGGER.debug("Songs to add to playlist: " + songs)

        url = "http://api.deezer.com/playlist/" + pid + "/tracks"+"?songs=" + songs + "&access_token=" + user['token'].encode('utf-8')
        try:
            request = Request(url, data="")
            LOGGER.debug("add_tracks_playlist::Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("add_tracks_playlist::Response: " + str(parsed_json))
        except URLError, e:
            LOGGER.error("Error while communating with the remote server : ", e)

    def get_all_tracks_from_playlist(self, pid):
        url = "http://api.deezer.com/playlist/" + pid + "/tracks"
        request = Request(url)

        try:
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("Response: " + str(parsed_json))
            tracks_title = []

            for t in parsed_json['data']:
                tracks_title.append(t)

            return tracks_title

        except URLError, e:
            LOGGER.error("Error while communicating with remote server :" , e)

    def get_track_ids_for_playlist(self, pid, token):
        url =  "http://api.deezer.com/playlist/" + pid + "/tracks?access_token=" + token.encode('utf-8')
        request = Request(url)

        try:
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("Response: " + str(parsed_json))
            tracks_ids = []

            for t in parsed_json['data']:
                tracks_ids.append(t['id'])

            return tracks_ids

        except URLError, e:
            LOGGER.error("Error while communicating with remote server :" , e)

    def logout(self, token):
        ##Call to DEEZER_LOGOUT_URL does not disconnect in the app
        LOGGER.info("Entering logout")
        url = DEEZER_LOGOUT_URL
        request = Request(url)
        LOGGER.debug("Requested url : " + url)
        try:
            response = urlopen(request)
            LOGGER.debug("LOGOUT::Opening url from request " + str(request))
            url = response.geturl()
            LOGGER.debug("LOGOUT::Requested url : " + url)
            request = Request(url)
            try:
                urlopen(request)
            except URLError, e:
                LOGGER.error("LOGOUT::Error while communicating with remote server :" , e)
        except URLError, e:
            LOGGER.error("LOGOUT::Error while communicating with remote server :" , e)
