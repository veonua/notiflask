from operator import contains
from flask_mail import Message
from notiflask import mail
from notiflask.gcm import send_to_user
from notiflask.glass_utils import Glass
from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User

__author__ = 'Veon'


def send_invitation(sender, email, name, data):
    invitation, created = Invitation.objects.get_or_create(email=email)
    invitation.save()
    invitation.name = name

    invitation_url = "http://secret-beach.herokuapp.com/invite/" + str(invitation.pk)
    android_url = "https://play.google.com/store/apps/details?id=com.veon.notify&feature=invitation_email"

    msg = Message("Friend Reminder",
                  sender="veon.ua@gmail.com",
                  recipients=[email])

    sname = str(invitation.name or "")
    msg.body = "Hello " + sname + ", Friend Reminder user sends you an invitation, \n"
    msg.html = "Hello " + sname + ", Friend Reminder user sends you an invitation,"

    if data is not None:
        msg.body += "\n " + data["title"] + "  " + data["text"]
        msg.html += "<br> <h3>" + data["title"] + "</h3>  <p>" + data["text"]

        url = data.get('canonicalUrl')
        if url is not None:
            msg.body += "\n " + url
            msg.html += "<a href='" + url + "'> link </a>"

        msg.html += "</p>"

    msg.body += "\n Start using Friend Reminder\nAndroid - " + android_url + "\nWeb - " + invitation_url
    msg.html += """<br><br>Start using Friend Reminder <br>
            <a href='""" + android_url + """'>Android app
            <img src="http://thedeadline.biz/App/Android.png" border="0" alt="Android App" width="200" height="75">
            </a> <br>
            <a href='""" + invitation_url + """'>Web</a>"""

    mail.send(msg)
    pass


def send(uid, data):
    if contains(uid, "@"):
        user = User.objects(email=uid.lower()).first()
        if user is not None and len(user.devices) > 0:
            Glass.send_mirror(user, data)
            return send_to_user(user, data)
        else:
            return send_invitation(None, uid, None, data)
    else:
        user = User.objects(pk=uid).first()
        if user is not None and len(user.devices) > 0:
            Glass.send_mirror(user, data)
            return send_to_user(user, data)
        else:
            return send_invitation(None, user.email, None, data)
