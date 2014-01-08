# http://www.fergalmoran.com/verifying-back-end-calls-from-android-using-python/
import json
import urllib2
import jwt

AUDIENCE_CLIENT_ID = "215543917772.apps.googleusercontent.com"


def get_data(token, client_id=None):
    """
    Try each key in turn until we find one that decrypts the token

    WARNING! doesn't verify tokens @see jwt.decode(verify=False)
    """

    def get_certs():
        """
        Grab the certificats from Google to decrypt the JWT token
        This really should cache the certs
        """
        req = urllib2.Request('https://www.googleapis.com/oauth2/v1/certs')
        f = urllib2.urlopen(req)
        return json.loads(f.read())

    _certs = get_certs()
    for key in _certs:
        try:
            token = jwt.decode(token, key=_certs[key], verify=False)
            if 'email' in token and 'aud' in token:
                if token['aud'] == AUDIENCE_CLIENT_ID and (
                    client_id == token['cid'] if client_id is not None else True):
                    return token

        except Exception, e:
            print "Error decoding: %s" % e.message

    return None