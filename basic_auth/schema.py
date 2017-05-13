"""Data schema for rest API methods."""

import colander

from .credential import BasicAuthCredentials


def valid_basic_auth(node, value):
    """Validator for Basic-Auth tokens."""
    try:
        BasicAuthCredentials.from_token(value)
    except ValueError as error:
        raise colander.Invalid(node, str(error))


class CredentialsCreateSchema(colander.MappingSchema):
    """Basic-Auth credentials create schema."""

    user = colander.SchemaNode(colander.String())
    token = colander.SchemaNode(
        colander.String(), validator=valid_basic_auth, missing=None)


class CredentialsUpdateSchema(colander.MappingSchema):
    """Basic-Auth credentials update schema."""

    token = colander.SchemaNode(
        colander.String(), validator=valid_basic_auth, missing=None)
