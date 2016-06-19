#coding: utf8

from flask.ext.wtf import Form
from wtforms import StringField, validators
from wtforms.validators import Required

class FusionForm(Form):
    playlist_code = StringField('playlist_code', [validators.Required()])
