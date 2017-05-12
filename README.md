# Basic authentication backend service

This service provides a REST API to manage basic-authentication credentials,
and an endpoint for validating credentials provided in a request.


## REST API

The rest API for managing credentials is availabile at the `/api` endpoint.


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
