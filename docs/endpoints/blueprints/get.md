# GET /blueprints
Retrieves a list of blueprints.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|List of Blueprints|Retrieval of Blueprints successful.

## Example
### Request
`GET /blueprints`
### Response body
```json
{
    "status": 200,
    "message": "Blueprints have been retrieved.",
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
