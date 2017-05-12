"""Data schema for rest API methods."""

import colander


def valid_basic_auth(node, value):
    """Validator for Basic-Auth tokens."""
    split = value.split(':')
    if len(split) != 2 or '' in split:
        raise colander.Invalid(
            node, 'Token must be in the form "<user>:<password>"')


class Credentials(colander.MappingSchema):
    """Basic-Auth credentials."""

    user = colander.SchemaNode(colander.String())
    token = colander.SchemaNode(
        colander.String(), validator=valid_basic_auth, missing=None)
