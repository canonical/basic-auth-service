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
    'colander',
    'pyYaml',
    'uvloop',
]

tests_require = [
    'asynctest',
    'fixtures',
]

config = {
    'name': 'basic-auth-service',
    'version': __version__,
    'description': description,
    'long_description': open('README.md').read(),
    'url': 'https://github.com/CanonicalLtd/basic-auth-service',
    'packages': find_packages(),
    'entry_points': {'console_scripts': [
        'basic-auth = basic_auth.server:main']},
    'test_suite': 'basic_auth',
    'install_requires': install_requires,
    'tests_require': tests_require,
    'extras_require': {'testing': tests_require}
}

setup(**config)
