"""API resource."""

import colander

from .error import InvalidResourceDetails


class ResourceCollection:
    """A resource collection."""

    def create(self, details):
        """Create a resource with specified details."""
        raise NotImplementedError('Subclasses must implement create()')

    def delete(self, res_id):
        """Delete the resource with specified ID."""
        raise NotImplementedError('Subclasses must implement delete()')

    def get(self, res_id):
        """Return the resource with specified ID."""
        raise NotImplementedError('Subclasses must implement get()')

    def update(self, res_id, details):
        """Update the resource with specified ID."""
        raise NotImplementedError('Subclasses must implement update()')


class APIResource:
    """An API resource.

    The collection parameter must be ResourceCollection subclass.

    The create_schema and update_schema parameters must be colander.Schema
    classes, used to validate input data for the corresponding operation.

    """

    def __init__(self, collection, create_schema, update_schema):
        self.collection = collection
        self.create_schema = create_schema
        self.update_schema = update_schema

    def create(self, data):
        """Create a resource from the specified details."""
        cleaned_data = self._clean_data(self.create_schema, data)
        return self.collection.create(cleaned_data)

    def delete(self, resource_id, data=None):
        """Delete a resource by ID."""
        return self.collection.delete(resource_id)

    def get(self, resource_id, data=None):
        """Return a resource by ID."""
        return self.collection.get(resource_id)

    def update(self, resource_id, data):
        """Update a resource."""
        cleaned_data = self._clean_data(self.update_schema, data)
        return self.collection.update(resource_id, cleaned_data)

    def _clean_data(self, schema_class, data):
        """Validate and clean input data."""
        try:
            return schema_class().deserialize(data)
        except colander.Invalid as error:
            messages = [
                '"{}": {}'.format(field, message)
                for field, message in error.asdict().items()]
            raise InvalidResourceDetails('Error: ' + ', '.join(messages))
