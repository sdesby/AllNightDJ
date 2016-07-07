from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required

class SignInForm(Form):
    new_user_name = StringField('new_user_name', [validators.Required()])
    new_user_mail = EmailField('new_user_mail', [validators.DataRequired(), validators.Email()])
    new_user_password = PasswordField('New Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
