from flask_mongoengine import Document
from mongoengine import StringField, EmailField

__author__ = 'Veon'


class Invitation(Document):
    name = StringField()
    email = EmailField(unique=True)

