from unittest import TestCase

from ..resource import (
    ResourceCollection,
    APIResource,
)
from ..sample import (
    SampleCreateSchema,
    SampleUpdateSchema,
    SampleResourceCollection,
)
from ..error import InvalidResourceDetails


class ResourceCollectionTest(TestCase):

    def setUp(self):
        super().setUp()
        self.collection = ResourceCollection()

    def test_create_not_implemented(self):
        """Subclasses must implement the create method."""
        self.assertRaises(NotImplementedError, self.collection.create, {})

    def test_delete_not_implemented(self):
        """Subclasses must implement the delete method."""
        self.assertRaises(NotImplementedError, self.collection.delete, 'x')

    def test_get_not_implemented(self):
        """Subclasses must implement the get method."""
        self.assertRaises(NotImplementedError, self.collection.get, 'x')

    def test_update_not_implemented(self):
        """Subclasses must implement the update method."""
        self.assertRaises(NotImplementedError, self.collection.update, 'x', {})


class APIResourceTest(TestCase):

    def setUp(self):
        super().setUp()
        self.collection = SampleResourceCollection()
        self.resource = APIResource(
            self.collection, SampleCreateSchema, SampleUpdateSchema)

    def test_create(self):
        "The create methods adds an item to the collection."
        data = {'id': 'foo', 'value': 'bar'}
        self.assertEqual(data, self.resource.create(data))
        self.assertEqual({'foo': data}, self.collection.items)

    def test_create_missing_field(self):
        """If a required field is missing, an error is raised."""
        # the "value" field is missing
        data = {'id': 'foo'}
        with self.assertRaises(InvalidResourceDetails) as cm:
            self.resource.create(data)
        self.assertEqual(
            'Error: "value": Required', str(cm.exception))

    def test_create_invalid_field(self):
        """If a field has an invalid value, an error is raised."""
        data = {'id': 33, 'value': 'foo'}
        with self.assertRaises(InvalidResourceDetails) as cm:
            self.resource.create(data)
        self.assertEqual(
            'Error: "id": 33 is not a string: {\'id\': \'\'}',
            str(cm.exception))

    def test_delete(self):
        "The delete methods removes an item from the collection."
        data = {'id': 'foo', 'value': 'bar'}
        self.collection.create(data)
        self.resource.delete('foo')
        self.assertEqual({}, self.collection.items)

    def test_get(self):
        """The get method returns an item from the collection."""
        data = {'id': 'foo', 'value': 'bar'}
        self.collection.create(data)
        self.assertEqual(data, self.resource.get('foo'))

    def test_update(self):
        """The update method updates details for the collection."""
        self.collection.create({'id': 'foo', 'value': 'bar'})
        updated = self.resource.update('foo', {'value': 'new'})
        self.assertEqual({'id': 'foo', 'value': 'new'}, updated)

    def test_update_missing_field(self):
        """If required fields are not specified, an error is raised,"""
        self.collection.create({'id': 'foo', 'value': 'bar'})
        with self.assertRaises(InvalidResourceDetails) as cm:
            self.resource.update('foo', {})
        self.assertEqual(
            'Error: "value": Required', str(cm.exception))
