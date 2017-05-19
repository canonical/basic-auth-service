from ..testing import HandlerTestCase
from ..handler import root


class RootTest(HandlerTestCase):

    async def test_root(self):
        """The root handler just returns info text."""
        response = await root(self.get_request())
        self.assertEqual(
            'HTTP basic-authorization backend and API service.', response.text)
