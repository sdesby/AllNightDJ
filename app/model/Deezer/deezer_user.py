from mongokit import Connection, Document
from ...db import database_init as db
from ...log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj")

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

class DeezerUser(Document):
    structure = {
    'id': int,
    'name':unicode,
    'email': unicode,
    'token': unicode,
    'tracklist': unicode,
    'allnightdjId': int
    }
    validators = {
    'name': max_length(50),
    'email': max_length(120),
    'token': max_length(120)
    }
    required_fields = ['id', 'name', 'email', 'token', 'tracklist']

    def store_user(self, parsed_json, token):
        LOGGER.info("Entering store_user")
        connection = db.connection()
        collection = connection['allnightdj'].deezerUser
        user = collection.DeezerUser()
        user['id'] = parsed_json['id']
        user['name'] = parsed_json['name']
        user['email'] = parsed_json['email']
        user['token'] = token
        user['tracklist'] = parsed_json['tracklist']
        #user['allnightdjId'] = allnightdjId
        user.save()
        LOGGER.info("Leaving store_user")
        return user

    def remove_user(self, token):
        LOGGER.info("Entering remove_user")
        connection = db.connection()
        collection = connection['allnightdj'].deezerUser
        collection.remove({'token': token})

    def find_user(self, token):
        LOGGER.info("Entering find_user()")
        connection = db.connection()
        collection = connection['allnightdj'].deezerUser
        user = collection.DeezerUser.find_one({'token': token})
        return user

    def store_applicationId(self, applicationId):
        LOGGER.info("Entering store_applicationId()")
        connection = db.connection()
        collection = connection['allnightdj'].deezerUser
        self['allnightdjId'] = applicationId
        self.save()

LOGGER.debug("Connection to DeezerUser in database")
c = db.connection()
c.register([DeezerUser])
