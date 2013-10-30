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


@app.route('/user/<uid>')
def get_user(uid):
    if contains(uid, "@"):
        user = User.objects(email=uid).first()
    else:
        user = User.objects(pk=uid).first()

    if user is None:
        abort(404)

    return render_template("user.html", email=user.email, devices=user.devices)


@app.route('/send', methods=['POST'])
def send():
    email = request.form['email']
    user = User.objects(email=email).first()
    devs = user.devices
    if devs is None:
        return redirect("/")

    dd = [dev.deviceId for dev in devs]
    data = {"message": request.form['message']}
    res = gcm_send_request(dd, data)
    return render_template('send_result.html', res=res)


@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run()