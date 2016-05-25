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

class Playlist(Document):
    structure = {
    'id':int,
    'title':unicode,
    'description': unicode,
    'duration': int,
    'nb_tracks': int,
    'link':unicode,
    'picture': unicode
    }
    validators = {
    'title': max_length(200),
    }
    required_fields = ['id', 'title', 'link']

    def __repr__(self):
        return "<Playlist %r>" % (self.title)

    def storePlaylists(self, parsed_json):
        LOGGER.info("Entering storePlaylist")
        connection = db.connection()
        collection = connection['allnightdj'].playlists
        playlists_as_json = parsed_json['data']

        for p in playlists_as_json:
            playlist = collection.Playlist()
            playlist['id'] = p['id']
            playlist['title'] = p['title']
            if 'description' in p.keys():
                playlist['description'] = p['description']
            playlist['duration'] = p['duration']
            playlist['nb_tracks'] = p['nb_tracks']
            playlist['link'] = p['link']
            playlist['picture'] = p['picture']
            playlist.save()

        LOGGER.info("Leaving storePlaylist")

    def findPlaylists(self):
        connection = db.connection()
        collection = connection['allnightdj'].playlists
        return collection.Playlist.find()

LOGGER.debug("Connection to Playlist in database")
c = db.connection()
c.register([Playlist])
