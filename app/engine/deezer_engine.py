from urllib2 import Request, urlopen, URLError
from urlparse import urlparse
import json
from ..model.user import User
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
        self.permissions = 'perms=basic_access,email'
        self.response_type="response_type=token"

    def getAuthentification(self):
        LOGGER.info("Entering getAuthentification function")
        url = self.AUTH_URL + "?" + self.APP_ID + "&" + self.redirect_uri + "&" + self.permissions

        try:
            LOGGER.debug("Requested url : " + url)
            return url

        except URLError, e:
            LOGGER.error("URLError with remote server :" , e)

    def getUser(self, code):
        LOGGER.info("Entering getUser")
        CODE_FOR_TOKEN = "code=" + code
        url_to_get_token = self.TOKEN_URL + "?" + self.APP_ID + "&" + self.APP_SECRET + "&" + CODE_FOR_TOKEN + "&output=json"
        LOGGER.debug("Requesting url: " + url_to_get_token)
        request = Request(url_to_get_token)
        response = urlopen(request)
        parsed_json = json.load(response)
        access_token = parsed_json["access_token"]

        LOGGER.info("Leaving getUser")
        return self.getUserWithToken(access_token)

    def getUserWithToken(self, token):
        LOGGER.info("Entering getUserWithToken")
        url = "http://api.deezer.com/user/me?access_token=" + token
        request = Request(url)

        try:
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("Response: ")
            LOGGER.debug(parsed_json)
            LOGGER.info("Leaving getUserWithToken")
            return self.storeUser(parsed_json, token)

        except URLError, e:
            print "Error while communicating with remote server :" , e

    def getPlaylistForUser(self, user):
        url = "http://api.deezer.com/user/me/playlists?access_token=" + user['token']
        request = Request(url)

        try:
            LOGGER.debug("Requested url : " + url)
            response = urlopen(request)
            parsed_json = json.loads(response.read())
            LOGGER.debug("Response: " + str(parsed_json))
            return parsed_json

        except URLError, e:
            print "Error while communicating with remote server :" , e


    def storeUser(self, parsed_json, token):
        LOGGER.info("Entering storeUser")
        connection = db.connection()
        collection = connection['allnightdj'].users
        user = collection.User()
        user['name'] = parsed_json["name"]
        user['email'] = parsed_json['email']
        user['token'] = token
        user['tracklist'] = parsed_json['tracklist']
        user.save()
        LOGGER.info("Leaving storeUser")
        return user

    def logout(self, token):
        ##Call to DEEZER_LOGOUT_URL does not disconnect in the app
        LOGGER.info("Entering logout")
        url = DEEZER_LOGOUT_URL
        request = Request(url)
        LOGGER.debug("Requested url : " + url)
        try:
            response = urlopen(request)
            print "**** RESPONSE ****"
            print response.getcode()
            print response.geturl()
            LOGGER.info("Opening url from request " + str(request))
            url = response.geturl()
            LOGGER.debug("Requested url : " + url)
            request = Request(url)
            try:
                urlopen(request)
            except URLError, e:
                print "Error while communicating with remote server :" , e
        except URLError, e:
            print "Error while communicating with remote server :" , e
