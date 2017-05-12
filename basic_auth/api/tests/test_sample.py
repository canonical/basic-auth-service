from unittest import TestCase

from ..sample import SampleResourceCollection
from ..error import (
    ResourceAlreadyExists,
    InvalidResourceDetails,
    ResourceNotFound,
)


class SampleResourceCollectionTest(TestCase):

    def setUp(self):
        super().setUp()
        self.collection = SampleResourceCollection()

    def test_create(self):
        """Resources can be created in the collection."""
        self.collection.create({'id': 'foo', 'bar': 'baz'})
        self.assertEqual({'foo': {'bar': 'baz'}}, self.collection.items)

    def test_create_duplicated(self):
        """Trying to create a resource with an existing ID raises an error."""
        self.collection.create({'id': 'foo', 'bar': 'baz'})
        self.assertRaises(
            ResourceAlreadyExists,
            self.collection.create, {'id': 'foo', 'boo': 'bza'})

    def test_create_missing_id(self):
        """If the "id" is missing from details, an error is raised."""
        self.assertRaises(
            InvalidResourceDetails, self.collection.create, {'foo': 'bar'})

    def test_delete(self):
        """A resouce can be deleted by ID."""
        self.collection.create({'id': 'foo', 'bar': 'baz'})
        self.collection.delete('foo')
        self.assertEqual({}, self.collection.items)

    def test_delete_not_found(self):
        """An error is raised if the ID is not found when deleting."""
        self.assertRaises(
            ResourceNotFound, self.collection.delete, "foo")

    def test_get(self):
        """Resources can be retrieved from the collection."""
        element = {'id': 'foo', 'bar': 'baz'}
        self.collection.create(element)
        self.assertEqual(element, self.collection.get('foo'))

    def test_get_not_found(self):
        """An error is raised if the ID is not found."""
        self.assertRaises(
            ResourceNotFound, self.collection.delete, "foo")

    def test_update(self):
        """A resource can be updated."""
        element = {'id': 'foo', 'bar': 'baz'}
        self.collection.create(element)
        updated = self.collection.update('foo', {'bar': 'new'})
        self.assertEqual({'id': 'foo', 'bar': 'new'}, updated)

    def test_update_not_found(self):
        """An error is raised if the ID is not found when updating."""
        self.assertRaises(
            ResourceNotFound, self.collection.update, "foo", {'bar': 'new'})
