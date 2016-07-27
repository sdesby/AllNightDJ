from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required

class LoginForm(Form):
    user_name = StringField('user_name', [validators.Required()])
    user_password = PasswordField('Password', [validators.DataRequired()])
