from flask import render_template, session
from notiflask import app
from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User
from notiflask.oauth.handler import login

__author__ = 'Veon'


def authorize():
    if '5274bb0ad7b36f1004e64fee' != session.get('userId'):
        return login()

# Views
@app.route('/admin/')
def admin_users():
    authorize()
    users = User.objects()
    return render_template("admin_index.html", users=users)


@app.route('/admin/invitations')
def admin_invitations():
    authorize()

    invitations = Invitation.objects()
    return render_template("admin_invitations.html", invitations=invitations)



