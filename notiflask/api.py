from flask_restful import Resource, reqparse
from notiflask import api
from notiflask.gcm import send_to_user
from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User
from notiflask.utils import send

__author__ = 'Veon'


class SendResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str)
        parser.add_argument('text', type=str)
        parser.add_argument('canonicalUrl', type=str, required=False)
        parser.add_argument('title', type=str, required=False)
        parser.add_argument('address', type=str, required=False)
        parser.add_argument('lat', type=float, required=False, ignore=True)
        parser.add_argument('lon', type=float, required=False, ignore=True)
        parser.add_argument('datetime', type=str, required=False)

        args = parser.parse_args()

        email = args['email'].lower()

        data = {
            "text": args['text'],
        }

        if args.get('canonicalUrl'):
            data["canonicalUrl"] = args['canonicalUrl']
        if args.get('title'):
            data["title"] = args['title']
        if args.get('address'):
            data['location'] = {
                "latitude": args['lat'],
                "longitude": args['lng'],
                "address": args['address'],
                "displayName": args['address']
            }
        if args.get('datetime'):
            #dt = iso8601.parse_date(request.form['datetime'])
            data['displayTime'] = args['datetime']

        data['menuItems'] = []
        data['menuItems'].append({
            "payload": "http://ya.ru",
            "action": "OPEN_URI"
        })

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