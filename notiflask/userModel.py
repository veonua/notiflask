from mongoengine import EmbeddedDocument, StringField, Document, ListField, EmbeddedDocumentField, EmailField, BooleanField

__author__ = 'veon'


class Device(EmbeddedDocument):
    deviceId = StringField()
    type = StringField(choices=("Android", "Glass", "iOS", "Browser"))
    manufacturer = StringField()
    model = StringField()


class User(Document):
    name = StringField()
    locale = StringField(max_length=2)
    gender = BooleanField()
    googleId = StringField()
    email = EmailField()
    devices = ListField(EmbeddedDocumentField(Device))

    meta = {
        'indexes': [
            {'fields': ['googleId'], 'sparse': True, 'unique': True},
            {'fields': ['email'],    'sparse': True, 'unique': True}
        ]
    }


