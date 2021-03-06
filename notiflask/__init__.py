from flask_mongoengine import MongoEngine
from flask import Flask
from flask_mail import Mail
from flask_restful import Api

__author__ = 'Veon'

app = Flask(__name__)
api = Api(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

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
import api
import admin
import oauth.handler