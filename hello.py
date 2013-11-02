import json
from operator import contains
import httplib2
from oauth2client.client import FlowExchangeError
from pymongo.errors import DuplicateKeyError
from gcm import gcm_send_request

from oauth.handler import create_oauth_flow
from userModel import User, Device

from flask import Flask, render_template, redirect, request, abort
from flask.ext.mongoengine import MongoEngine
import util


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '208861662943.apps.googleusercontent.com',
    'consumer_secret': 'nk0M_wTfQBnPG1Ku4iuA4mpo'
}

# MongoDB Config
app.config['MONGODB_SETTINGS'] = {
    'DB': 'main',
    "host": 'mongodb://python:mongopython@ds051378.mongolab.com:51378/heroku_app18792506'
}
# Create database connection object
db = MongoEngine(app)

@app.before_first_request
def init():
    #User.drop_collection()
    pass

# Views
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/params/<int:_id>')
def params(_id=0):
    return "This is '" + str(_id) + "'"


@app.route('/register_device/<deviceId>', methods=['GET', 'POST'])
def register_device(deviceId):
    if request.method == 'GET':
        return render_template("register_device.html", deviceId=deviceId)
    if request.method == 'POST':
        userEmail = request.form['userEmail']
        if userEmail is None:
            abort(400)
        user, created = User.objects.get_or_create(email=userEmail)
        newDevice = Device(deviceId=deviceId)
        user.devices.append(newDevice)
        user.save()
        return redirect("/user/" + userEmail)


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


def sendToUser(user, data):
    dd = [dev.deviceId for dev in user.devices]
    return gcm_send_request(dd, data)


@app.route('/send', methods=['POST'])
def send():
    email = request.form['email']
    user = User.objects(email=email).first()

    data = {"message": request.form['message']}
    res = sendToUser(user, data)

    return render_template('send_result.html', res=res)


@app.route('/github/<uid>', methods=['POST'])
def github_hook(uid):
    payload = json.loads(request.form['payload'])
    name = payload['pusher']['name'] + "(" + payload['pusher']['email'] + ")"
    uri = payload['repository']['url']

    user = getUser(uid)
    data = {'message': name,
            'uri': uri}

    sendToUser(user, data)
    return "ok"


@app.route('/auth')
def auth():
    flow = create_oauth_flow(request)
    flow.params['approval_prompt'] = 'force'
    uri = flow.step1_get_authorize_url()
    # Perform the redirect.
    return redirect(str(uri))


def CreateService(service, version, creds):
    http = httplib2.Http()
    creds.authorize(http)
    return build(service, version, http=http)


@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code', '')
    if not code:
        abort(400)

    oauth_flow = create_oauth_flow(request)
    # Perform the exchange of the code. If there is a failure with exchanging
    # the code, return None.
    try:
        creds = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        abort(400)

    users_service = util.create_service('oauth2', 'v2', creds)
    # TODO: Check for errors.
    guser = users_service.userinfo().get().execute()

    user, created = User.objects.get_or_create(googleId=guser.get('id'))
    if created:
        user.email = guser.get('email')
        user.gender = guser.get('gender') == 'male'
    user.locale = guser.get('locale')

    try:
        user.save()
    except DuplicateKeyError as e:
        return "Duplicate "+str(e)

    return redirect("/user/"+str(user.pk))


if __name__ == '__main__':
    app.run()