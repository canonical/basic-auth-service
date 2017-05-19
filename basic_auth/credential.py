"""Basic-auth credentials."""

from collections import namedtuple
import random
import string


_BasicAuthCredentials = namedtuple(
    'BasicAuthCredentials', ['username', 'password'])


class BasicAuthCredentials(_BasicAuthCredentials):
    """Basic authorization credentials."""

    @classmethod
    def generate(cls):
        """Generate random BasicAuthCredentials."""
        return cls(generate_random_token(), generate_random_token())

    @classmethod
    def from_token(cls, token):
        """create BasicAuthCredentials from a "user:password" token."""
        split = token.split(':')
        if len(split) != 2 or '' in split:
            raise ValueError(
                'Token must be in the form "user:password"')
        return cls(*split)

    def __str__(self):
        return '{}:{}'.format(self.username, self.password)


def generate_random_token(length=20):
    """Generate a random string to use as token."""
    choices = string.ascii_letters + string.digits
    return "".join(random.choice(choices) for _ in range(length))
