from mongoengine import EmbeddedDocument, StringField, Document, ListField, EmbeddedDocumentField, EmailField

__author__ = 'veon'


class Device(EmbeddedDocument):
    deviceId = StringField()


class User(Document):
    email = EmailField(unique=True)
    devices = ListField(EmbeddedDocumentField(Device))


