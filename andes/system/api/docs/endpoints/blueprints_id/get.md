# GET /blueprints/<_id>
Retrieves a specific blueprint according to passed ID.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Blueprint|Retrieval of Blueprint successful.
400|null|Blueprint not found.

## Example
### Request
`GET /blueprints/1`
### Response body
```json
{
    "status": 201,
    "message": "Blueprint foo has been retrieved.",
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
