from flask import session
from flask_restful import Resource, reqparse
from flask_restful.types import boolean
from notiflask import api
from notiflask.google_id import get_data
from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User, Device
from notiflask.oauth.handler import oauth2callback
from notiflask.util import getUser
from notiflask.utils import send

__author__ = 'Veon'


class SendResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str)
        parser.add_argument('text', type=unicode)
        parser.add_argument('canonicalUrl', type=str, required=False)
        parser.add_argument('title', type=unicode, required=False)
        parser.add_argument('address', type=unicode, required=False)
        parser.add_argument('showConfirmation', type=boolean, default=False)
        parser.add_argument('latitude', type=float, required=False, ignore=True)
        parser.add_argument('longitude', type=float, required=False, ignore=True)
        parser.add_argument('displayTime', type=str, required=False)
        args = parser.parse_args()

        sender_id = session.get("userId")
        if not sender_id:
            parser2 = reqparse.RequestParser()
            parser2.add_argument('Google-Token', type=str, location='headers')
            data = get_data(parser2.parse_args()["Google-Token"])
            sender = User.objects(email=data['email'].lower()).first()
        else:
            sender = User.objects(pk=sender_id).first()

        if not sender:
            return 'invalid user', 403

        email = args['email'].lower()
        data = {
            "text": args['text'],
        }

        if args.get('canonicalUrl'):
            data["canonicalUrl"] = args['canonicalUrl']
        if args.get('title'):
            data["title"] = args['title']
        else:
            data["title"] = sender.name

        if args.get('address'):
            data['location'] = {
                "latitude": args['latitude'],
                "longitude": args['longitude'],
                "address": args['address'],
                "displayName": args['address']
            }
        if args.get('displayTime'):
            #dt = iso8601.parse_date(request.form['datetime'])
            data['displayTime'] = args['displayTime']

        if args['showConfirmation']:
            data['showConfirmation'] = True

        # data['menuItems'] = []
        # data['menuItems'].append({
        #     "payload": "http://ya.ru",
        #     "action": "OPEN_URI"
        # })

        res = send(email, data)
        return res


api.add_resource(SendResource, '/api/v1/send', '/send')


class InvitationResource(Resource):
    def get(self, key):
        i = Invitation.objects(pk=key).first()
        return {"name": i.name, "email": i.email}

    def delete(self, key):
        Invitation.objects(pk=key).delete()
        return '', 204


api.add_resource(InvitationResource, '/api/v1/invitation/<string:key>')


class UserResource(Resource):
    def get(self, key):
        i = User.objects(pk=key).first()
        return {"name": i.name, "email": i.email}

    def delete(self, key):
        User.objects(pk=key).delete()
        return '', 204


api.add_resource(UserResource, '/api/v1/user/<string:key>')


class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Google-Token', type=str, location='headers')
        args = parser.parse_args()
        data = get_data(args["Google-Token"])

        if data is None:
            return 'invalid token', 403

        email = data['email']
        user = User.objects(email=email.lower()).first()

        if user is None or user.auth is None:
            return 'new user, start permission request', 401

        session['userId'] = str(user.pk)
        session['user'] = {'name': user.name, 'email': user.email}
        return "", 204


api.add_resource(LoginResource, '/api/v1/login')


class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code', type=str)
        args = parser.parse_args()
        code = args["code"]

        oauth2callback(code, False)
        return "", 204


api.add_resource(SignupResource, '/api/v1/oauth_callback')


class DeviceResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Google-Token', type=str, location='headers')
        parser.add_argument('id', type=str)
        parser.add_argument('model', type=unicode)
        parser.add_argument('manufacturer', type=unicode)
        args = parser.parse_args()
        data = get_data(args["Google-Token"])

        user = getUser(data['email'])

        model = args.get('model')
        manufacturer = args.get('manufacturer')
        device_id = args.get('id')

        dev = next((d for d in user.devices if d['deviceId'] == device_id), None)
        #hasDevice = any(d['deviceId'] == device_id for d in user.devices)

        if not dev:
            user.devices.append(Device(deviceId=device_id, type="Android", model=model, manufacturer=manufacturer))
            code = 201
        else:
            dev.deviceId = device_id
            code = 204

        user.save()
        return "", code


api.add_resource(DeviceResource, '/api/v1/device')