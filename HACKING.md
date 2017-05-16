# Hacking

The basic-auth service uses `tox` for development.

Every function is run as a separate `tox` target, to keep application, testing
and tools dependencies separated.

## Running the server

Run the server with `tox -e run`.

A simple client to interact with the server API is available at
`dev/api-client`.


## Runing tests

Tests can be run with just `tox`.

This will run unittests and lint. To only run tests, use `tox -e py35`

Alternatively, coverage tests can be run with `tox -e coverage`, which also
prints out the coverage report at the end.


## Linting

Linting can be performed with `tox -e lint`.
