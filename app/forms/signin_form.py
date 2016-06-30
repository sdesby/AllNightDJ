from flask.ext.wtf import Form
from wtforms import StringField, validators
from wtforms.validators import Required

class SignInForm(Form):
    new_user_name = StringField('new_user_name', [validators.Required()])
    new_user_mail = StringField('new_user_mail', [validators.Required()])
