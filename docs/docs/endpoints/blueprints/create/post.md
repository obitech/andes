# POST /blueprints/create
Creates a new blueprint.

## Headers
* `Authorization: JWT <JWT Token>`
* `Content-Type: application/json`

## Body
Key | JSON Value type | Required
---|---|---
name|String|Yes
image|String|Yes
description|String|No

## Returns
Status code | Data | Comments 
---|---|---
201|Blueprint|Blueprint has been created successfully.
400|null|Blueprint with passed image already exists.

## Example
### Request
`POST /blueprints/create`
### Request body
```json
{
    "name": "foo",
    "description": "bar",
    "image": "hello-world"
}
```
### Response body
```json
{
    "status": 201,
    "message": "Blueprint foo has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo",
        "description": "bar",
        "image": "hello-world",
        "services: [1,2]
    }
}
```