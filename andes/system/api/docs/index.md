# Welcome

Welcome to Andes' API documentation. For information on classes and functions themselves, please refer to the source for now.

* [Github repo](https://hub.docker.com/r/obitech/andes-api/)
* [Docker image](https://hub.docker.com/r/obitech/andes-api/)

## General

Responses return, in general, a JSON object with metadata and (if applicable) the actual data or an error message in the following format:

```json
# Sample format
{
    "status": <status code>,
    "message": <...>,
    "error": <...>,
    "data": <...>
}
```

## Authentication

If you're starting from scratch you need to create a user first:
```
# Endpoint
POST /register

# Header
Content-Type: application/json

# Body
{
    "username": "foo",
    "password": "bar"
}
```

Now you need to authenticate: 
```
# Endpoint
POST /auth

#Header
Content-Type: application/json

# Body
{
    "username": "foo",
    "password": "bar"
}
```

Which will return a JWT token:
```
{
  "access_token": superSecretToken
}
```

This needs to be included in following requests as a header:
```
# Endpoint
GET /stacks

# Header
Authorization: JWT superSecretToken

# Response
{
    "status": 200,
    "message": "Stacks have been retrieved.",
    "error": null,
    "data": []
}
```
