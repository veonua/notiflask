from flask import redirect, session
from flask_restful import abort
from notiflask import app
from notiflask.models.userModel import Device
from notiflask.oauth.mstorage import MongoStorage
from notiflask.util import create_service, getUser

__author__ = 'Veon'


class Glass(object):
    DEVICE_ID = 'GoogleGlassId'

    @staticmethod
    def has_glass_connected(user):
        return any(d['deviceId'] == Glass.DEVICE_ID for d in user.devices)


    @staticmethod
    def send_mirror(user, data):
        if not Glass.has_glass_connected(user):
            return

        try:
            creds = MongoStorage(user).get()

            body = data
            body['notification'] = {'level': 'DEFAULT'}

            mirror_service = create_service('mirror', 'v1', creds)
            return mirror_service.timeline().insert(body=body).execute()

        except Exception, e:
            print "Error sending mirror: %s" % e.message


@app.route('/user/connect_glass', methods=['POST'])
def connect_glass():
    if 'userId' not in session:
        abort(403)

    user = getUser(session['userId'])
    model = "Glass"
    manufacturer = "Google"
    _type = "Glass"

    hasDevice = Glass.has_glass_connected(user)

    if not hasDevice:
        user.devices.append(Device(deviceId=Glass.DEVICE_ID, type=_type, model=model, manufacturer=manufacturer))
        user.save()
    return redirect("/")
