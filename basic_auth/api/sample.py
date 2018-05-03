"""Sample/testing API implementation classes."""

from copy import deepcopy
import operator

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

    def __init__(self, id_field='id'):
        self.id_field = id_field
        self.items = {}

    async def create(self, details):
        resource_details = deepcopy(details)
        try:
            res_id = resource_details.pop(self.id_field)
        except KeyError:
            raise InvalidResourceDetails(
                'Missing "{}" for the resource'.format(self.id_field))
        if res_id in self.items:
            raise ResourceAlreadyExists(res_id)
        self.items[res_id] = resource_details
        # Retruned details include the resource ID
        return res_id, details

    async def get_all(self, *args, **kwargs):
        return sorted((
            self._copy_and_add_id(k, {'username': v['token'].split(':')[0]})
            for k, v in self.items.items()
        ), key=operator.itemgetter('username'))

    async def delete(self, res_id):
        try:
            del self.items[res_id]
        except KeyError:
            raise ResourceNotFound(res_id)

    async def get(self, res_id):
        item = self._get(res_id)
        return self._copy_and_add_id(res_id, item)

    async def update(self, res_id, details):
        item = self._get(res_id)
        item.update(details)

        return self._copy_and_add_id(res_id, item)

    def _get(self, res_id):
        try:
            return self.items[res_id]
        except KeyError:
            raise ResourceNotFound(res_id)

    def _copy_and_add_id(self, res_id, item):
        details = deepcopy(item)
        details[self.id_field] = res_id
        return details
