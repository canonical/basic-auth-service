"""REST API resource errors."""

import logging
import traceback

from .response import APIError


class ResourceError(Exception):
    """Base class for resource-related errors."""

    # The HTTP error this exception maps to.  Subclasses can set a different
    # one.
    http_error = 'InternalServerError'


class ResourceAlreadyExists(ResourceError):
    """A resource with the same ID already exists."""

    http_error = 'Conflict'

    def __init__(self, res_id):
        super().__init__(
            'A resource with ID "{}" already exists'.format(res_id))


class ResourceNotFound(ResourceError):
    """A resource with the specified ID can't be found."""

    http_error = 'NotFound'

    def __init__(self, res_id):
        super().__init__(
            'Resource with ID "{}" not found'.format(res_id))


class InvalidResourceDetails(ResourceError):
    """Provided details for the resource are invalid."""

    http_error = 'BadRequest'


def to_api_error(error):
    """Convert resource errors to proper APIErrors.

    Unknown errors are converted to 500 errors.

    """
    if isinstance(error, ResourceError):
        return APIError(error.http_error, message=str(error))

    # Log the error since it's likely an application issue
    logger = logging.getLogger()
    logger.error(traceback.format_exc())
    return APIError(
        'InternalServerError', message='A server error has occurred')
