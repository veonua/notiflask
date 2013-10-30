import json
from operator import contains
from gcm import gcm_send_request
from userModel import User, Device
from flask import Flask, render_template, redirect, request, abort
from flask.ext.mongoengine import MongoEngine

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

# Views
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/params/<int:_id>')
def params( _id = 0):
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
        return redirect("/user/"+userEmail)


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
    uri = payload['repository']['uri']

    user = getUser(uid)
    data = {'message': name,
            'uri': uri}

    sendToUser(user, data)
    return "ok"


@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run()