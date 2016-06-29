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

    def find_playlists(self):
        connection = db.connection()
        collection = connection['allnightdj'].playlists
        return collection.Playlist.find()

    def find_playlist_with_title(self, title):
        connection = db.connection()
        collection = connection['allnightdj'].playlists
        return collection.find_one({'title': title})

    def find_playlist_with_id(self, playlist_id):
        playlists = self.find_playlists()
        pl = Playlist()
        for p in playlists:
            if str(p['id']) == str(playlist_id):
                pl = p
                LOGGER.info("find_playlist_with_id::Found playlist : " + pl['title'])
        return pl

    def find_playlists_by_ids(self, ids):
        playlists = []
        for i in ids:
            p = self.find_playlist_with_id(i)
            playlists.append(p)
        LOGGER.info("find_playlists_by_ids::Found playlist : " + p['title'])
        return playlists

    def already_has_playlist(self):
        p = self.find_playlists()
        if p.count() > 0:
            LOGGER.info("Playlists have been found")
            return True
        else:
            LOGGER.info("No playlists have been found")
            return False

    def remove_playlists(self):
        LOGGER.info("Entering remove_playlists")
        connection = db.connection()
        collection = connection['allnightdj'].playlists
        collection.remove({})

LOGGER.debug("Connection to Playlist in database")
c = db.connection()
c.register([Playlist])
