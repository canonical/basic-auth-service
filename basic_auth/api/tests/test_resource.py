import asynctest

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


class ResourceCollectionTest(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.collection = ResourceCollection()

    async def test_create_not_implemented(self):
        """Subclasses must implement the create method."""
        with self.assertRaises(NotImplementedError):
            await self.collection.create({})

    async def test_delete_not_implemented(self):
        """Subclasses must implement the delete method."""
        with self.assertRaises(NotImplementedError):
            await self.collection.delete('x')

    async def test_get_not_implemented(self):
        """Subclasses must implement the get method."""
        with self.assertRaises(NotImplementedError):
            await self.collection.get('x')

    async def test_update_not_implemented(self):
        """Subclasses must implement the update method."""
        with self.assertRaises(NotImplementedError):
            await self.collection.update('x', {})


class APIResourceTest(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.collection = SampleResourceCollection()
        self.resource = APIResource(
            self.collection, SampleCreateSchema, SampleUpdateSchema)

    async def test_create(self):
        "The create methods adds an item to the collection."
        data = {'id': 'foo', 'value': 'bar'}
        res_id, details = await self.resource.create(data)
        self.assertEqual('foo', res_id)
        self.assertEqual(data, details)
        self.assertEqual({'foo': {'value': 'bar'}}, self.collection.items)

    async def test_create_missing_field(self):
        """If a required field is missing, an error is raised."""
        # the "value" field is missing
        data = {'id': 'foo'}
        with self.assertRaises(InvalidResourceDetails) as cm:
            await self.resource.create(data)
        self.assertEqual(
            'Error: "value": Required', str(cm.exception))

    async def test_create_invalid_field(self):
        """If a field has an invalid value, an error is raised."""
        data = {'id': 33, 'value': 'foo'}
        with self.assertRaises(InvalidResourceDetails) as cm:
            await self.resource.create(data)
        self.assertEqual(
            'Error: "id": 33 is not a string: {\'id\': \'\'}',
            str(cm.exception))

    async def test_get_all(self):
        """The get_all method returns all items from the collection."""
        await self.collection.create({'id': 'foo', 'token': 'foo:bar'})
        await self.collection.create({'id': 'baz', 'token': 'baz:qux'})
        self.assertEqual((
            {'id': 'baz', 'username': 'baz'},
            {'id': 'foo', 'username': 'foo'},
        ), await self.resource.get_all())

    async def test_delete(self):
        "The delete methods removes an item from the collection."
        data = {'id': 'foo', 'value': 'bar'}
        await self.collection.create(data)
        await self.resource.delete('foo')
        self.assertEqual({}, self.collection.items)

    async def test_get(self):
        """The get method returns an item from the collection."""
        data = {'id': 'foo', 'value': 'bar'}
        await self.collection.create(data)
        self.assertEqual(data, await self.resource.get('foo'))

    async def test_update(self):
        """The update method updates details for the collection."""
        await self.collection.create({'id': 'foo', 'value': 'bar'})
        updated = await self.resource.update('foo', {'value': 'new'})
        self.assertEqual({'id': 'foo', 'value': 'new'}, updated)

    async def test_update_missing_field(self):
        """If required fields are not specified, an error is raised."""
        await self.collection.create({'id': 'foo', 'value': 'bar'})
        with self.assertRaises(InvalidResourceDetails) as cm:
            await self.resource.update('foo', {})
        self.assertEqual(
            'Error: "value": Required', str(cm.exception))
