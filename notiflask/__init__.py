from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask import Flask
from flask_mail import Mail

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

# e-mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'noreply@thesendr.com'
app.config['MAIL_PASSWORD'] = 'noreply123'

mail = Mail(app)

# administrator list
ADMINS = ['veon.ua@gmail.com']

import hello
import oauth.handler