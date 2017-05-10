"""API resource."""


class APIResource:
    """An API resource."""

    def __init__(self, schema, collection):
        self.schema = schema
        self.collection = collection

    def create(self, details):
        """Create a resource from the specified details."""
        return details  # XXX

    def get(self, resource_id, content=None):
        """Return a resource by ID."""
        return {'id': resource_id}  # XXX
