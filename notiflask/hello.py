import json

from flask import render_template, redirect, request, abort, session, Response
from notiflask.glass_utils import Glass

from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User, Device
from notiflask.oauth.handler import login
from notiflask import app
from notiflask.util import getUser
from notiflask.utils import send_invitation, send


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


@app.route('/invite/<uid>')
def invitation(uid):
    invite = Invitation.objects(pk=uid).first()
    if invite is None:
        abort(403)

    return render_template("invite.html", key=invite.pk, email=invite.email.lower(), name=invite.name)


@app.route('/user/invite', methods=['POST'])
def invite_user():
    email = request.form['email'].lower()
    if 'userId' not in session:
        pass

    send_invitation(None, email, name=request.form['name'])
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


@app.route('/user/<uid>')
def get_user(uid):
    user = getUser(uid)

    if user is None:
        return render_template("user404.html", email=uid)

    return render_template("user.html", own=(str(user.pk) == session.get('userId')), email=user.email.lower(),
                           devices=user.devices, glassConnected=Glass.has_glass_connected(user))


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

    data = {'title': name,
            'text': text + " in " + branch + " " + reponame,
            'canonicalUrl': uri}

    send(uid, data)
    return Response(status=204)


if __name__ == '__main__':
    app.run()