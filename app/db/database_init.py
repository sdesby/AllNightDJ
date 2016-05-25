from flask import Flask
from mongokit import Connection

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

connect = Connection(app.config['MONGODB_HOST'],
                    app.config['MONGODB_PORT'])
# connect to the database
def connection():
    return connect

#def register(toRegister):
#    connect.register([toRegister])
