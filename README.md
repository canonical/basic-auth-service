# HTTP Basic authorization backend service

This service provides a REST API to manage basic-authorization credentials,
and an endpoint for validating credentials provided in a request.


## REST API

The REST API for managing credentials is availabile at the `/api` endpoint.

See the [API docs](API.md) for details on API calls.

### API credentials

The REST API requires basic-authorization for access.

Credentials for API access can be managed with the `manage-credentials` script.
This allows adding, removing and listing credentials.
As an example:

```bash
$ ./manage-credentials add myuser --description 'a user'
+----------+------------+-------------+
| Username | Password   | Description |
+----------+------------+-------------+
| myuser   | uXaQtXJV6q | a user      |
+----------+------------+-------------+
$ ./manage-credentials list
+----------+------------+-------------+
| Username | Password   | Description |
+----------+------------+-------------+
| myuser   | uXaQtXJV6q | a user      |
| youruser | vVnPzo4HMR |             |
+----------+------------+-------------+
$ ./manage-credentials remove myuser
```

## Credentials validation

The validation endpoint is presented at `/auth-check` and returns an empty
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

    # this location is protected by basic-auth 
    location /secret {
        auth_request /auth;
    }

    location = /auth {
        proxy_pass http://auth_backend/auth-check/;
    }
```
