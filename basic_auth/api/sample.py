"""Sample/testing API implementation classes."""

import colander

from .resource import ResourceCollection
from .error import (
    ResourceAlreadyExists,
    ResourceNotFound,
    InvalidResourceDetails,
)


class SampleCreateSchema(colander.MappingSchema):
    """Sample schema for resource creation."""

    id = colander.SchemaNode(colander.String())
    value = colander.SchemaNode(colander.String())


class SampleUpdateSchema(colander.MappingSchema):
    """Sample schema for resource update."""

    value = colander.SchemaNode(colander.String())


class SampleResourceCollection(ResourceCollection):
    """An in-memory ResourceCollection."""

    def __init__(self):
        self.items = {}

    def create(self, details):
        try:
            res_id = details['id']
        except KeyError:
            raise InvalidResourceDetails('Missing "id" for the resource')
        if res_id in self.items:
            raise ResourceAlreadyExists(res_id)
        self.items[res_id] = details
        return details

    def delete(self, res_id):
        try:
            del self.items[res_id]
        except KeyError:
            raise ResourceNotFound(res_id)

    def get(self, res_id):
        try:
            return self.items[res_id]
        except KeyError:
            raise ResourceNotFound(res_id)

    def update(self, res_id, details):
        item = self.get(res_id)
        item.update(details)
        return item
