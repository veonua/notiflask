from flask import render_template, session
from notiflask import app
from notiflask.models.invitationModel import Invitation
from notiflask.models.userModel import User
from notiflask.oauth.handler import login

__author__ = 'Veon'

# Views
@app.route('/admin/')
def admin_users():
    if 'userId' not in session:
        return login()

    users = User.objects()
    return render_template("admin_index.html", users=users)


@app.route('/admin/invitations')
def admin_invitations():
    if 'userId' not in session:
        return login()

    invitations = Invitation.objects()
    return render_template("admin_invitations.html", invitations=invitations)



