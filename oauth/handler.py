from oauth2client.client import flow_from_clientsecrets

SCOPES = ('https://www.googleapis.com/auth/glass.timeline '
          'https://www.googleapis.com/auth/glass.location '
          'https://www.googleapis.com/auth/userinfo.profile '
          'https://www.googleapis.com/auth/userinfo.email ')


def create_oauth_flow(request=None):
    """Create OAuth2.0 flow controller."""
    flow = flow_from_clientsecrets('client_secrets.json', scope=SCOPES)

    flow.redirect_uri = '%soauth2callback' % request.url_root
    return flow
