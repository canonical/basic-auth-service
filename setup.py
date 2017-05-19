from setuptools import (
    setup,
    find_packages,
)

from basic_auth import (
    __version__,
    __doc__ as description,
)


install_requires = [
    'aiohttp',
    'alembic',
    'aiopg',
    'colander',
    'prettytable',
    'psycopg2',
    'pyYaml',
    'sqlalchemy',
    'uvloop',
]

tests_require = [
    'asynctest',
    'fixtures',
    'testresources',
]

config = {
    'name': 'basic-auth-service',
    'version': __version__,
    'description': description,
    'long_description': open('README.md').read(),
    'url': 'https://github.com/CanonicalLtd/basic-auth-service',
    'packages': find_packages(),
    'package_data': {'basic_auth': ['alembic/*', 'alembic/versions/*']},
    'entry_points': {'console_scripts': [
        'basic-auth = basic_auth.script.server:main',
        'manage-credentials = basic_auth.script.manage_credentials:main']},
    'test_suite': 'basic_auth',
    'install_requires': install_requires,
    'tests_require': tests_require,
    'extras_require': {'testing': tests_require}
}

setup(**config)
