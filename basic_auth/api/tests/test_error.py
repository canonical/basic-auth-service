import json

import fixtures

from ..error import (
    ResourceAlreadyExists,
    ResourceNotFound,
    to_api_error)


class ToAPIErrorTest(fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.useFixture(fixtures.LoggerFixture())

    def test_from_resource_error_already_exists(self):
        """ResourceAlreadyExists is converted to an HTTP Conflict."""
        error = to_api_error(ResourceAlreadyExists('foo'))
        self.assertEqual(409, error.status)
        self.assertEqual(
            {'code': 'Conflict',
             'message': 'A resource with ID "foo" already exists'},
            json.loads(error.text))

    def test_from_resource_error_not_found(self):
        """ResourceNotFound is converted to an HTTP NotFound."""
        error = to_api_error(ResourceNotFound('foo'))
        self.assertEqual(404, error.status)
        self.assertEqual(
            {'code': 'Not Found',
             'message': 'Resource with ID "foo" not found'},
            json.loads(error.text))

    def test_from_other_error(self):
        """Other errors are converted to InternalServerError."""
        error = to_api_error(Exception('something went wrong'))
        self.assertEqual(500, error.status)
        self.assertEqual(
            {'code': 'Internal Server Error',
             'message': 'A server error has occurred'},
            json.loads(error.text))
