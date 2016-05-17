from mongokit import Connection, Document
from ..db import database_init as db
from ..log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj")

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

class User(Document):
    structure = {
    'name':unicode,
    'email': unicode,
    'token': unicode,
    'tracklist': unicode
    }
    validators = {
    'name': max_length(50),
    'email': max_length(120),
    'token': max_length(120)
    }
    required_fields = ['name', 'email', 'token', 'tracklist']

    def __repr__(self):
        return "<User %r>" % (self.name)

LOGGER.debug("Connection to User database")
c = db.connection()
c.register([User])
