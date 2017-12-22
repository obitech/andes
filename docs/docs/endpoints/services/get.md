# GET /services
Retrieves a list of services.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|List of Services|Retrieval of Services has been successful.

## Example
### Request
`GET /services`
### Response body
```json
{
    "status": 200,
    "message": "Services have been retrieved.",
    "error": null,
    "data": [
        {
            "id": 1,
            "blueprint": 1,
            "name": "foo_service",
            "description": "A test service",
            "stacks": [],
            "exposed_ports": [
                80,
                8080
            ],
            "mapped_ports": [
                "80:80"
            ],
            "volumes": [
                "/srv/www:/"
            ],
            "env": [
                "FOO=BAR",
                "DEBUG=1"
            ],
            "restart": "always",
            "ip": "172.42.0.11"
        }
    ]
}
```
