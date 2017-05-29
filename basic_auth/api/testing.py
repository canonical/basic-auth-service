from aiohttp.test_utils import AioHTTPTestCase

from ..testing import (
    HandlerTestCase,
    basic_auth_header,
)


class APITestCase(HandlerTestCase):

    def get_request(self, path='/', method='GET', content=None,
                    auth=None, content_type='application/json',
                    headers=None, json_encode=True):
        """Make an API request."""
        return super().get_request(
            path=path, method=method, content=content, auth=auth,
            headers=headers, content_type=content_type,
            json_encode=json_encode)


class APIApplicationTestCase(AioHTTPTestCase):

    async def client_request(self, method='GET', path='/', auth=None,
                             content_type='application/json', **kwargs):
        """Make a request through the client."""
        headers = kwargs.setdefault('headers', {})
        headers['Content-Type'] = content_type
        if auth is not None:
            headers.update(basic_auth_header(*auth))
        return await self.client.request(method, path, **kwargs)
