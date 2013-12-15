import json
from operator import contains

from flask import render_template, redirect, request, abort, session, jsonify, Response

from notiflask.gcm import send_to_user
from notiflask.oauth.handler import login
from notiflask.userModel import User, Device
from flask.ext.mongoengine import MongoEngine
from notiflask import app, mail
from flask_mail import Message


@app.before_first_request
def init():
    #User.drop_collection()
    pass


# Views
@app.route('/')
def home():
    if 'userId' in session:
        return redirect("/user/" + session['userId'])

    return render_template('index.html')


@app.route('/user/invite', methods=['GET', 'POST'])
def invite_user():
    email = request.form['email']
    invitation_url = "http://secret-beach.herokuapp.com/invitation/" + email
    android_url = "https://play.google.com/store/apps/details?id=com.veon.notify&feature=invitation_email"

    msg = Message("Invitation to the notify",
                  sender="veon.ua@gmail.com",
                  recipients=[email])

    msg.body = "User sends you invitation to notify, \n" \
               "Android - " + android_url + "\n" \
                                            "Web - " + invitation_url

    msg.html = "User sends you invitation to notify, <br>" \
               "<div style='overflow:hidden; height:70px;'>" \
               "  <a href='" + android_url + "'>" \
                                             "     <img style='width: 200px; margin-top: -79px; opacity: 0.5;' " \
                                             "      src='http://twentyfiveentertainment.com/wp-content/themes/Starkers/images/googleplay.png'" \
                                             "      alt='Andorid'>" \
                                             "  </a>" \
                                             "</div>" \
                                             "<a href='" + invitation_url + "'>Web</a>"

    mail.send(msg)
    return redirect("/")


@app.route('/user/remove')
def remove_device():
    if 'userId' not in session:
        abort(403)

    user_id = session['userId']
    device_id = request.args.get('device')

    User.objects(pk=user_id).update_one(pull__devices={'deviceId': device_id})
    return redirect("/user/" + user_id)


@app.route('/register_device/<device_id>', methods=['GET', 'POST'])
def register_device(device_id):
    if request.method == 'GET':
        if 'userId' not in session:
            return login()

        return render_template("register_device.html", deviceId=device_id, userName=session['user']['name'])
    if request.method == 'POST':
        if 'userId' not in session:
            abort(403)

        user, created = User.objects.get_or_create(pk=session['userId'])

        model = request.args.get('model')
        manufacturer = request.args.get('manufacturer')

        hasDevice = any(d['deviceId'] == device_id for d in user.devices)

        if not hasDevice:
            user.devices.append(Device(deviceId=device_id, type="Android", model=model, manufacturer=manufacturer))
            user.save()
        return redirect("/")


def getUser(uid):
    if contains(uid, "@"):
        return User.objects(email=uid).first()
    else:
        return User.objects(pk=uid).first()


@app.route('/user/<uid>')
def get_user(uid):
    user = getUser(uid)

    if user is None:
        return render_template("user404.html", email=uid)

    return render_template("user.html", own=(str(user.pk) == session.get('userId')), email=user.email,
                           devices=user.devices)


@app.route('/send', methods=['POST'])
def send():
    email = request.form['email']
    user = User.objects(email=email).first()

    data = {
        "text": request.form['text'],
    }

    if request.form['canonicalUrl']:
        data["canonicalUrl"] = request.form['canonicalUrl']
    if request.form['title']:
        data["title"] = request.form['title']
    if request.form['address']:
        data['location'] = {
            "latitude": request.form['lat'],
            "longitude": request.form['lng'],
            "address": request.form['address'],
            "displayName": request.form['address']
        }
    if request.form['datetime']:
        #dt = iso8601.parse_date(request.form['datetime'])
        data['displayTime'] = request.form['datetime']

    data['menuItems'] = []
    data['menuItems'].append({
        "id": "uid",
        "payload": "http://ya.ru",
        "action": "OPEN_URI",
        "displayName": "action1",
    })

    res = send_to_user(user, data)

    return jsonify(res)


@app.route('/github/<uid>', methods=['POST'])
def github_hook(uid):
    payload = json.loads(request.form['payload'])
    name = payload['pusher']['name'] + "(" + payload['pusher']['email'] + ")"
    uri = payload['repository']['url']
    reponame = payload['repository']['name']
    commits = payload['commits']
    cnum = len(commits)
    if cnum == 1:
        text = commits[0]["message"]
    else:
        text = str(cnum) + " commits"

    branch = payload['ref']

    user = getUser(uid)
    data = {'title': name,
            'text': text + " in " + branch + " " + reponame,
            'canonicalUrl': uri}

    send_to_user(user, data)
    return Response(status=204)


if __name__ == '__main__':
    app.run()