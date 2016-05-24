from ..model.user import User
from ..db import database_init as db

from ..log_configurator import allnightdj_logger as log

LOGGER = log.get_logger("DB Engine")

def findUser(token):
    LOGGER.info("Entering findUser()")
    connection = db.connection()
    collection = connection['allnightdj'].users
    user = collection.User.find_one({'token': token})
    return user
