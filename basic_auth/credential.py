"""Basic-auth credentials."""

from collections import namedtuple
import random
import string
import hashlib


_BasicAuthCredentials = namedtuple(
    'BasicAuthCredentials', ['username', 'password'])


class BasicAuthCredentials(_BasicAuthCredentials):
    """Basic authentication credentials."""

    @classmethod
    def generate(cls):
        """Generate random BasicAuthCredentials."""
        return cls(cls._random_token(), cls._random_token())

    @classmethod
    def from_token(cls, token):
        """create BasicAuthCredentials from a "user:password" token."""
        split = token.split(':')
        if len(split) != 2 or '' in split:
            raise ValueError(
                'Token must be in the form "user:password"')
        return cls(*split)

    @staticmethod
    def _random_token():
        choices = string.ascii_letters + string.digits
        text = "".join(random.choice(choices) for _ in range(64))
        return hashlib.sha1(text.encode('ascii')).hexdigest()

    def __str__(self):
        return '{}:{}'.format(self.username, self.password)
