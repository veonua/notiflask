import urllib2
from urlparse import urlparse
import httplib2

from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from pymongo.errors import DuplicateKeyError
from flask import redirect, request, abort, session
from notiflask import util, app
from notiflask.models.invitationModel import Invitation

from notiflask.models.userModel import User
from flask.ext.mongoengine import MongoEngine
from notiflask.oauth.mstorage import MongoStorage
from notiflask.util import getUser


SCOPES = ('https://www.googleapis.com/auth/glass.timeline '
          'https://www.googleapis.com/auth/glass.location '
          'https://www.googleapis.com/auth/userinfo.profile '
          'https://www.googleapis.com/auth/userinfo.email ')


def create_oauth_flow():
    """Create OAuth2.0 flow controller."""
    flow = flow_from_clientsecrets('client_secrets.json', scope=SCOPES)

    flow.redirect_uri = '%soauth2callback' % request.url_root
    return flow


def login():
    return redirect('/auth?referrer=' + urllib2.quote(request.full_path))


@app.route('/auth')
def auth():
    flow = create_oauth_flow()
    key = request.args.get('key', None)
    if key is not None:
        Invitation.objects(pk=key).delete()
    elif request.args.get('referrer', None) is not None:
        flow.params['state'] = request.args.get('referrer', None)
    elif request.referrer is not None:
        parsed = urlparse(request.referrer)
        flow.params['state'] = urllib2.quote(parsed.path)

    uri = flow.step1_get_authorize_url()
    # Perform the redirect.
    return redirect(str(uri))


@app.route('/logout')
def logout():
    try:
        user = getUser(session['userId'])
        creds = MongoStorage(user).get()
        http = httplib2.Http()
        creds.refresh(http)
        creds.revoke(http)
    except Exception as e:
        pass

    session.pop('userId', None)
    session.pop('user', None)
    return redirect("/")


@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code', '')
    if not code:
        abort(400)

    oauth_flow = create_oauth_flow()
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
    storage = MongoStorage(user)
    creds.set_store(storage)

    if created:
        user.email = guser.get('email')
        user.gender = guser.get('gender') == 'male'
    user.locale = guser.get('locale')
    user.name = guser.get('name')

    try:
        storage.put(creds)
    except DuplicateKeyError as e:
        return "Duplicate " + str(e)

    session['userId'] = str(user.pk)
    session['user'] = {'name': user.name, 'email': user.email}

    state = request.args.get('state', None)
    if state is None:
        return redirect("/")
    return redirect(urllib2.unquote(state))