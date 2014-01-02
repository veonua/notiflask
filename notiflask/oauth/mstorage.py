from oauth2client.client import Storage, OAuth2Credentials

__author__ = 'Veon'


class MongoStorage(Storage):
    def __init__(self, user):
        self._user = user

    def locked_get(self):
        """Retrieve credential.

      The Storage lock must be held when this is called.

      Returns:
        oauth2client.client.Credentials
      """
        credential = OAuth2Credentials.new_from_json(self._user.auth)
        if credential:
            credential.set_store(self)
        return credential

    def locked_put(self, credentials):
        """Write a credential.

      The Storage lock must be held when this is called.

      Args:
        credentials: Credentials, the credentials to store.
      """
        self._user.auth = credentials.to_json()
        self._user.save()

    def locked_delete(self):
        """Delete a credential.

      The Storage lock must be held when this is called.

      Args:
        credentials: Credentials, the credentials to store.
      """
        self._user.auth = None
        self._user.save()
