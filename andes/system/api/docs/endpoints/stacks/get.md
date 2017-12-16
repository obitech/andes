# GET /stacks
Retrieves a list of stacks.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|List of stacks|Retrieval of stacks has been successful.

## Example
### Request
`GET /stacks`
### Response body
```json
{
    "status": 200,
    "message": "Stacks have been retrieved.",
    "error": null,
    "data": [
        {
            "id": 1,
            "name": "foo_stack",
            "description": "test stack",
            "subdomain": "test.example.com",
            "services": [
                1
            ],
            "active": false,
            "created_at": "2017-12-16T18:15:12.179471",
            "last_changed": "2017-12-16T18:15:12.179471"
        }
    ]
}
```
