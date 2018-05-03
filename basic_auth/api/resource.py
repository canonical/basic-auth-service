"""API resource."""

import colander

from .error import InvalidResourceDetails


class ResourceCollection:
    """A resource collection."""

    async def create(self, details):
        """Create a resource with specified details.

        This method must return a 2-tuple with the resource ID and
        representation as dict.
        """
        raise NotImplementedError('Subclasses must implement create()')

    async def get_all(self):
        """Return all resources.

        The response will have the password fragment of the token redacted.
        """
        raise NotImplementedError('Subclasses must implement get_all()')

    async def delete(self, res_id):
        """Delete the resource with specified ID.

        This method should return nothing.
        """
        raise NotImplementedError('Subclasses must implement delete()')

    async def get(self, res_id):
        """Return the resource with specified ID.

        This method must return a dict with the resource details.
        """
        raise NotImplementedError('Subclasses must implement get()')

    async def update(self, res_id, details):
        """Update the resource with specified ID.

        This method must return a dict with updated resource details.
        """
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

    async def create(self, data):
        """Create a resource from the specified details."""
        cleaned_data = self._clean_data(self.create_schema, data)
        return await self.collection.create(cleaned_data)

    async def get_all(self, data=None, start_date=None, end_date=None):
        """List all resources."""
        return tuple(await self.collection.get_all(
            start_date=start_date, end_date=end_date))

    async def delete(self, resource_id, data=None):
        """Delete a resource by ID."""
        await self.collection.delete(resource_id)

    async def get(self, resource_id, data=None):
        """Return a resource by ID."""
        return await self.collection.get(resource_id)

    async def update(self, resource_id, data):
        """Update a resource."""
        cleaned_data = self._clean_data(self.update_schema, data)
        return await self.collection.update(resource_id, cleaned_data)

    def _clean_data(self, schema_class, data):
        """Validate and clean input data."""
        try:
            return schema_class().deserialize(data)
        except colander.Invalid as error:
            messages = [
                '"{}": {}'.format(field, message)
                for field, message in error.asdict().items()]
            raise InvalidResourceDetails('Error: ' + ', '.join(messages))
