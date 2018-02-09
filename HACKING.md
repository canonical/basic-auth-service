# Hacking

The basic-auth service uses `tox` for development.

Every function is run as a separate `tox` target, to keep application, testing
and tools dependencies separated.

# Setting up the development environment

Run `make deps setup`: this will install all system level dependencies and
set up both the configuration files and the database.

## Running the server

Run the server with `tox -e run`.

Auth credentials for accessing the API can be added with the following command:
`.tox/py35/bin/manage-credentials add {username}`. The command will output the
username and password to use for HTTP basic auth (see below).

A simple client to interact with the server API is available at
`dev/api-client`. For instance:
```
dev/api-client --creds admin:37kxFAIWp2eG4aErZXqA credentials add user=who
dev/api-client --creds admin:37kxFAIWp2eG4aErZXqA credentials list
```
.

## Runing tests

Tests can be run with just `tox`.

This will run unittests and lint. To only run tests, use `tox -e py35`

Alternatively, coverage tests can be run with `tox -e coverage`, which also
prints out the coverage report at the end.

System are run separately from unittests, with `tox -e system-test`.

## Linting

Linting can be performed with `tox -e lint`.
