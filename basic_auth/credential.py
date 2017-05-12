"""Basic-auth credentials."""

from collections import namedtuple
import random
import string
import hashlib


_BasicAuthCredentials = namedtuple(
    'BasicAuthCredentials', ['user', 'password'])


class BasicAuthCredentials(_BasicAuthCredentials):
    """Basic authentication credentials."""

    @classmethod
    def generate(cls):
        """Generate random BasicAuthCredentials."""
        return cls(cls._random_token(), cls._random_token())

    @staticmethod
    def _random_token():
        choices = string.ascii_letters + string.digits
        text = "".join(random.choice(choices) for _ in range(64))
        return hashlib.sha1(text.encode('ascii')).hexdigest()

    def __str__(self):
        return '{}:{}'.format(self.user, self.password)
