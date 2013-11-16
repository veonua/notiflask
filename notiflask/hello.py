import json
from operator import contains

from flask import render_template, redirect, request, abort, session

from notiflask.gcm import gcm_send_request, send_to_user
from notiflask.oauth.handler import login
from notiflask.userModel import User, Device
from flask.ext.mongoengine import MongoEngine
from notiflask import app


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
        abort(404)

    return render_template("user.html", email=user.email, devices=user.devices)


@app.route('/send', methods=['POST'])
def send():
    email = request.form['email']
    user = User.objects(email=email).first()

    data = {"text": request.form['message']}
    res = send_to_user(user, data)

    return render_template('send_result.html', res=res)


@app.route('/github/<uid>', methods=['POST'])
def github_hook(uid):
    payload = json.loads(request.form['payload'])
    name = payload['pusher']['name'] + "(" + payload['pusher']['email'] + ")"
    uri = payload['repository']['url']

    user = getUser(uid)
    data = {'title': name,
            'text': name,
            'uri': uri}

    send_to_user(user, data)
    return "ok"


if __name__ == '__main__':
    app.run()