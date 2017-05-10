# Basic authentication backend service

This service provides a REST API to manage basic-authentication credentials,
and an endpoint for validating credentials provided in a request.

It can be used as backend for providing Basic-Auth to web servers, by forwarding requests to it.
The authentication endpoint will just return `200` in case of valid credentials, `401` otherwise.

The following a sample configuration for the [Nginx][http://nginx.org/] web server:

```
upstream auth_backend {
    server localhost:8080;
}

server {

    # ... other server config

    location /secret {
        auth_request /auth;
    }

    location = /auth {
        proxy_pass http://auth_backend/check;
    }
````
