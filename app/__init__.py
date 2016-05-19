from flask import Flask

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"
app.config['SECRET_KEY'] = "granmerkal"

from app import views
