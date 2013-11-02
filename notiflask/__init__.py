from flask_mongoengine import MongoEngine
from flask import Flask

__author__ = 'Veon'

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '208861662943.apps.googleusercontent.com',
    'consumer_secret': 'nk0M_wTfQBnPG1Ku4iuA4mpo'
}

# MongoDB Config
app.config['MONGODB_SETTINGS'] = {
    'DB': 'main',
    "host": 'mongodb://python:mongopython@ds051378.mongolab.com:51378/heroku_app18792506'
}
# Create database connection object
db = MongoEngine(app)

import hello
import oauth.handler