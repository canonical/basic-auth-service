# REST API

The basic-auth service provides a REST API for managing user credentials.

The API can be accessed at the `/api` endpoint.


## Performing calls

Authentication to the API service itself is performed through
basic-authorization (credentials for the API are separate from the ones managed
by the service).

Payload for API requests and response is JSON, and the Content-Type for
requests must be set to `application/json;profile=basic-auth.api;version=1.0`.

An example call to create a user is the following:

```
curl -H 'Content-Type: application/json;profile=basic-auth.api;version=1.0' \
     -X POST http://user:pass@hostname/api/credentials \
     -d '{"user": "foo"}'
```


### Resources and calls

The following resources and calls are available in the API:


### Credentials

Credentials map a user to a token representing its basic auth credentials (in
the `username:password` form).

The `user` is a unique string that has no special meaning for the service
itself, so callers can be use any string .

The `token` can be either provided or generated automatically from the service.


Calls related to credentials are the following:

| Endpoint              | Method | Description                    |
| ----------------------|--------|--------------------------------|
| `/credentials`        | GET    | List all credentials           |
| `/credentials`        | POST   | Create a user with credentials |
| `/credentials/<user>` | GET    | Return user credentials        |
| `/credentials/<user>` | PUT    | Update user credentials        |
| `/credentials/<user>` | DELETE | Delete user credentials        |


#### GET /credentials

List all user credentials, with the password fragment of the code redacted.

The **request** doesn't require a body. The **response** lists user details,
ordered alphabetically by token (username), such as:

```json
[
  {"user": "who", "username": "adfasadfasdfa3f23fa4F"},
  {"user": "rose", "username": "bjdhoNafkdaDps438u3df"}
]
```

The following HTTP codes can be set in responses:

- `200 OK`: normal response.


#### POST /credentials

Create user credentials.

The **request** body must as follows:

```json
{"user": "my-user"}
```
and the **response** will contain the generated token:

```json
{"user": "my-user",
 "token": "sdfasadfasdfa3f23fa4F:f4af3gf3aqkh34hg98h"}
```

The **request** body can also provide a token in the form `username:password`:

```json
{"user": "my-user",
 "token": "foo:bar"}
```

The following HTTP codes can be set in responses:

- `201 Created`: credentials have been created
- `409 Conflict`: a user with the specified name already exists
- `400 Bad Request`: the request is invalid, either user or token format are
  invalid


#### GET /credentials/\<user\>

Return credentials for a user.

The **request** doesn't require a body, as the requested user is specified in
the url, for instance `/credentials/my-user`.

The **response** contains user details, such as:

```json
{"user": "my-user", "token":
 "sdfasadfasdfa3f23fa4F:f4af3gf3aqkh34hg98h"}
```

The following HTTP codes can be set in responses:

- `200 OK`: normal response, user details are returned in body
- `404 Not Found`: the requested user is not found


#### DELETE /credentials/\<user\>

Delete user credentials.

The **request** doesn't require a body, as the requested user is specified in
the url, for instance `/credentials/my-user`.

The **response** is an empty JSON object:

```json
{}
```

The following HTTP codes can be set in responses:

- `200 OK`: normal response, user have been removed
- `404 Not Found`: the requested user is not found


#### PUT /credentials/\<user\>

Update credentials for an existing user.

The **request** body can be an empty JSON object

```json
{}
```

in which case a new token is generated for the user, or it can specify a token:

```json
{"token": "foo:bar"}
```

The **response** contains updated credentials:

```json
{"user": "my-user",
 "token": "sdfasadfasdfa3f23fa4F:f4af3gf3aqkh34hg98h"}
```

The following HTTP codes can be set in responses:

- `200 OK`: normal response, user have been removed
- `404 Not Found`: the requested user is not found
- `400 Bad Request`: the specified token format is invalid
