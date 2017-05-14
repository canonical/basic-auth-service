import asynctest

from ..sample import SampleResourceCollection
from ..error import (
    ResourceAlreadyExists,
    InvalidResourceDetails,
    ResourceNotFound,
)


class SampleResourceCollectionTest(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.collection = SampleResourceCollection()

    async def test_create(self):
        """Resources can be created in the collection."""
        data = {'id': 'foo', 'bar': 'baz'}
        res_id, details = await self.collection.create(data)
        self.assertEqual('foo', res_id)
        self.assertEqual(data, details)
        self.assertEqual({'foo': {'bar': 'baz'}}, self.collection.items)

    async def test_create_duplicated(self):
        """Trying to create a resource with an existing ID raises an error."""
        await self.collection.create({'id': 'foo', 'bar': 'baz'})
        with self.assertRaises(ResourceAlreadyExists):
            await self.collection.create({'id': 'foo', 'boo': 'bza'})

    async def test_create_missing_id(self):
        """If the "id" is missing from details, an error is raised."""
        with self.assertRaises(InvalidResourceDetails):
            await self.collection.create({'foo': 'bar'})

    async def test_delete(self):
        """A resouce can be deleted by ID."""
        await self.collection.create({'id': 'foo', 'bar': 'baz'})
        await self.collection.delete('foo')
        self.assertEqual({}, self.collection.items)

    async def test_delete_not_found(self):
        """An error is raised if the ID is not found when deleting."""
        with self.assertRaises(ResourceNotFound):
            await self.collection.delete("foo")

    async def test_get(self):
        """Resources can be retrieved from the collection."""
        element = {'id': 'foo', 'bar': 'baz'}
        await self.collection.create(element)
        self.assertEqual(element, await self.collection.get('foo'))

    async def test_get_not_found(self):
        """An error is raised if the ID is not found."""
        with self.assertRaises(ResourceNotFound):
            await self.collection.delete("foo")

    async def test_update(self):
        """A resource can be updated."""
        element = {'id': 'foo', 'bar': 'baz'}
        await self.collection.create(element)
        updated = await self.collection.update('foo', {'bar': 'new'})
        self.assertEqual({'id': 'foo', 'bar': 'new'}, updated)

    async def test_update_not_found(self):
        """An error is raised if the ID is not found when updating."""
        with self.assertRaises(ResourceNotFound):
            await self.collection.update("foo", {'bar': 'new'})
