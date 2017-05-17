# Basic authentication backend service

This service provides a REST API to manage basic-authentication credentials,
and an endpoint for validating credentials provided in a request.


## REST API

The REST API for managing credentials is availabile at the `/api` endpoint.

See the [API docs](API.md) for details on API calls.

### API credentials

The REST API requires basic-authentication for access.

Credentials for API access can be managed with the `manage-credentials` script.
This allows adding, removing and listing credentials.
As an example:

```bash
$ ./manage-credentials add myuser mysecret --description 'a user'
$ ./manage-credentials list
+----------+----------+-------------+
| Username | Password | Description |
+----------+----------+-------------+
| myuser   | mysecret | a user      |
+----------+----------+-------------+
$ ./manage-credentials remove myuser
Action succeeded
```

## Authentication validation

The authentication endpoint is presented at `/auth-check` and returns an empty
response with the following HTTP codes:

- `200` for valid credentials
- `401` for invalid credentials

This endpoint can be used to integrate the application with web servers; the
following snippet shows an example for the [Nginx](http://nginx.org/) web
server:

```
upstream auth_backend {
    server localhost:8080;
}

server {

    # ... other server config

    # this location is protected by authentication 
    location /secret {
        auth_request /auth;
    }

    location = /auth {
        proxy_pass http://auth_backend/auth-check/;
    }
```
