# GET /stacks/<_id>
Retrieves a specific stack according to passed ID.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Stack|Retrieval of stack successful.
400|null|Stack with passed name has not been found.

## Example
### Request
`GET /stacks/1`
### Response body
```json
{
    "status": 200,
    "message": "Stack foo_stack has been retrieved.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo_stack",
        "description": "test stack",
        "subdomain": "test.example.com",
        "services": [1],
        "created_at": "2017-12-14T09:21:50.503274",
        "last_changed": "2017-12-14T09:21:50.503274"
    }
}
```
