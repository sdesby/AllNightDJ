from flask.ext.wtf import Form
from wtforms import StringField, validators
from wtforms.validators import Required

class NewPlaylistForm(Form):
    new_playlist_name = StringField('new_playlist_name', [validators.Required()])
