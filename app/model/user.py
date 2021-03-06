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
    'name': unicode,
    'email': unicode,
    'pass': unicode
    }
    validators = {
    'name': max_length(50),
    'email': max_length(120),
    }
    required_fields = ['name', 'email', 'pass']

    def __repr__(self):
        return "<User %r>" % (self.name)

    def create_new_user(self, new_user_name, new_user_mail, new_user_password):
        LOGGER.info("Entering create_new_user")
        connection = db.connection()
        collection = connection['allnightdj'].users
        user = collection.User()
        all_users = self.find_all_users()
        user['id'] = all_users.count()
        user['name'] = new_user_name
        user['email'] = new_user_mail
        user['pass'] = unicode(hash_pass(new_user_password))
        user.save()
        LOGGER.info("User with id " + str(user['id']) + " has been created")
        LOGGER.info("Leaving create_new_user")
        return user

    def find_all_users(self):
        LOGGER.info("Entering find_all_users")
        connection = db.connection()
        collection = connection['allnightdj'].users
        all_users = collection.User.find()
        return all_users

    def already_exists(self, user_name, user_password):
        LOGGER.info("Entering already_exists")
        user = self.find_one_user(user_name, user_password)
        if user is None:
            return False
        else:
            return True

    def find_one_user(self, user_name, user_password):
        LOGGER.info("Entering User::find_one")
        connection = db.connection()
        collection = connection['allnightdj'].users
        LOGGER.debug("Querying for user " + user_name + " with pass " + unicode(hash_pass(user_password)))
        return collection.User.find_one({'name': user_name, 'pass': unicode(hash_pass(user_password))})


def hash_pass(password):
    # used to hash the password similar to how MySQL hashes passwords with the password() function.
    import hashlib
    hash_password = hashlib.sha1(password.encode('utf-8')).digest()
    hash_password = hashlib.sha1(hash_password).hexdigest()
    return hash_password

LOGGER.debug("Connection to User in database")
c = db.connection()
c.register([User])
