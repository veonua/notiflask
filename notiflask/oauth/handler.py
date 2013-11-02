from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from pymongo.errors import DuplicateKeyError
from flask import redirect, request, abort, session
from notiflask import util

from notiflask.hello import app
from notiflask.userModel import User
from flask.ext.mongoengine import MongoEngine


SCOPES = ('https://www.googleapis.com/auth/glass.timeline '
          'https://www.googleapis.com/auth/glass.location '
          'https://www.googleapis.com/auth/userinfo.profile '
          'https://www.googleapis.com/auth/userinfo.email ')


def create_oauth_flow(request=None):
    """Create OAuth2.0 flow controller."""
    flow = flow_from_clientsecrets('client_secrets.json', scope=SCOPES)

    flow.redirect_uri = '%soauth2callback' % request.url_root
    return flow


@app.route('/auth')
def auth():
    flow = create_oauth_flow(request)
    flow.params['approval_prompt'] = 'force'
    uri = flow.step1_get_authorize_url()
    # Perform the redirect.
    return redirect(str(uri))


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
    user.name = guser.get('name')

    try:
        user.save()
    except DuplicateKeyError as e:
        return "Duplicate "+str(e)

    session['userId'] = str(user.pk)
    session['user'] = {'name': user.name, 'email': user.email}

    return redirect("/")