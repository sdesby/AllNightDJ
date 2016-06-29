from mongokit import Connection, Document
from ..db import database_init as db
from ..log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj:user")

class User(Document):
    structure = {
    'id': int,
    'name':unicode,
    'email': unicode,
    }
    validators = {
    'name': max_length(50),
    'email': max_length(120),
    }
    required_fields = ['id', 'name', 'email']

    def __repr__(self):
        return "<User %r>" % (self.name)
