# POST /stacks/create
Creates a new stack.

## Headers
* `Authorization: JWT <JWT Token>`
* `Content-Type: application/json`

## Body
Key | JSON Value type | Comment | Required
---|---|---|---
name|String|The stack name|Yes
description|String|The stack description|No
subdomain|String|The subdomain this stack will be reachable under.|No

## Returns
Status code | Data | Comments 
---|---|---
201|Stack|Stack has been created successfully.
400|null|Stack with passed name already exists.

## Example
### Request
`POST /stacks/create`
### Request body
```json
{
    "name": "foo_stack",
    "description": "test stack",
    "subdomain": "test.example.com",
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
        "services": [1],
        "active": false,
        "created_at": "2017-12-14T09:21:50.503274",
        "last_changed": "2017-12-14T09:21:50.503274"
    }
}
```