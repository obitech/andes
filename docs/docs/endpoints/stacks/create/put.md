# PUT /stacks/create
Creates or updates a stack.

## Headers
* `Authorization: JWT <JWT Token>`
* `Content-Type: application/json`

## Body
Key | JSON Value type | Comment | Required
---|---|---|---
name|String|The stack name|Yes
description|String|The stack description|No
subdomain|String|The subdomain this stack will be reachable under.|No
email|String|The email to be put in the stack-specific Caddyfile. This is needed for automatic TLS encryption.|No
proxy_service|Integer|The service ID to which Caddy should forward requests to. Needs to be part of the stack|No
proxy_port|Integer|The port added to the service ID for Caddy to forward requests to. **This does not check if the service actually publishes the port.**|No

## Returns
Status code | Data | Comments 
---|---|---
201|Stack|Stack has been created or updated successfully.
400|null|Stack with passed name already exists.

## Example
### Request
`PUT /stacks/create`
### Request body
```json
{
    "name": "foo_stack",
    "description": "test stack",
    "subdomain": "test.example.com",
    "email": "test@example.com",
    "proxy_service": 1,
    "proxy_port": 80,    
    "services": [1]
}
```
### Response body
```json
{
    "status": 201,
    "message": "Stack foo_stack has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo_stack",
        "description": "test stack",
        "subdomain": "test.example.com",
        "email": "test@example.com",
        "proxy_service": 1,
        "proxy_port": 80,
        "services": [1],
        "created_at": "2017-12-14T09:21:50.503274",
        "last_changed": "2017-12-14T09:21:50.503274"
    }
}
```