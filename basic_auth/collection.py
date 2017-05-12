"""Collection for Basic-Auth credentials."""

from .credential import BasicAuthCredentials
from .api.sample import SampleResourceCollection


# XXX use the in-memory collection for now
class CredentialsCollection(SampleResourceCollection):
    """Collection for Basic-Auth credentials."""

    def __init__(self):
        super().__init__(id_field='user')

    def create(self, details):
        if not details['token']:
            details['token'] = str(BasicAuthCredentials.generate())
        return super().create(details)

    def update(self, resource_id, details):
        if not details['token']:
            details['token'] = str(BasicAuthCredentials.generate())
        return super().update(resource_id, details)

    def credentials_match(self, user, password):
        """Return whether the provided user/password match."""
        credentials = [details['token'] for details in self.items.values()]
        return '{}:{}'.format(user, password) in credentials
