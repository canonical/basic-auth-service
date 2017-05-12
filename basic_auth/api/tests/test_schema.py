from unittest import TestCase

from colander import Invalid

from ..schema import valid_basic_auth


class ValidBasicAuthTest(TestCase):

    def test_valid_format(self):
        """The validator returns None if the format is valid."""
        self.assertIsNone(valid_basic_auth(None, "user:pass"))

    def test_missing_user(self):
        """The validator raises an error if the user is missing."""
        self.assertRaises(Invalid, valid_basic_auth, None, ":pass")

    def test_missing_password(self):
        """The validator raises an error if the password is missing."""
        self.assertRaises(Invalid, valid_basic_auth, None, "user:")

    def test_too_many_tokens(self):
        """The validator raises an error if more than one : is present."""
        self.assertRaises(Invalid, valid_basic_auth, None, "user:pass:other")
