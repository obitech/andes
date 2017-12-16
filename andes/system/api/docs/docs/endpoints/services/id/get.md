# GET /services/<_id>
Retrieves a specific service according to passed ID.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Service|Retrieval of Service successful.
400|null|Service with passed name has not been found.

## Example
### Request
`GET /services/1`
### Response body
```json
{
    "status": 201,
    "message": "Service foo_service has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "blueprint": 1,
        "name": "foo_service",
        "description": "A test service",
        "stacks": [1],
        "exposed_ports": [80,8080],
        "mapped_ports": ["80:80"],
        "volumes": ["/srv/www:/"],
        "env": ["FOO=BAR","DEBUG=1"],
        "ip": "172.42.0.11"
    }
}
```
