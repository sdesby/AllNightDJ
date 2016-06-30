from mongokit import Connection, Document
from ..db import database_init as db
from ..log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("allnightdj:user")

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

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
    required_fields = ['name', 'email']

    def __repr__(self):
        return "<User %r>" % (self.name)

    def create_new_user(self, new_user_name, new_user_mail):
        LOGGER.info("Entering create_new_user")
        connection = db.connection()
        collection = connection['allnightdj'].users
        user = collection.User()

        all_users = self.find_all_users();
        user['id'] = all_users.count()
        user['name'] = new_user_name
        user['email'] = new_user_mail
        user.save()
        print "**** New User Id ****"
        print user['id']
        LOGGER.info("Leaving create_new_user")
        return user

    def find_all_users(self):
        LOGGER.info("Entering find_all_users")
        connection = db.connection()
        collection = connection['allnightdj'].users
        all_users = collection.User.find()
        return all_users

LOGGER.debug("Connection to User in database")
c = db.connection()
c.register([User])
