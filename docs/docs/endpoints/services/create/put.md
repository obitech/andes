# PUT /services/create
Creates or updates a service.

## Headers
* `Authorization: JWT <JWT Token>`
* `Content-Type: application/json`

## Body
Key | JSON Value type | Comment | Required
---|---|---|---
name|String|The service name|Yes
blueprint|Integer|The Blueprint ID this service implements|Yes
description|String|The service description|No
exposed_ports|Array of integers|Ports to be [exposed](https://docs.docker.com/compose/compose-file/#expose) to other services in stack.|No
mapped_ports|Array of strings|Ports to be [mapped](https://docs.docker.com/compose/compose-file/#ports) between host and service|No
volumes|Array of strings|Volumes to be [mapped](https://docs.docker.com/compose/compose-file/#short-syntax-3) between host and service. Only supports file system mapping.|No
env|Array of strings|Environment variables to be passed to service|No
restart|String|The restart flag for this service|No


## Returns
Status code | Data | Comments 
---|---|---
201|Service|Service has been created or updated successfully.
400|null|Service with passed name already exists.

## Example
### Request
`PUT /services/create`
### Request body
```json
{
    "name": "foo_service",
    "description": "A test service",
    "exposed_ports": [80,8080],
    "mapped_ports": ["80:80"],
    "blueprint": 1,
    "volumes": ["/srv/www:/"],
    "env": ["FOO=BAR","DEBUG=1"],
    "restart": "always",
    "stacks": 1
}
```
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
        "restart": "always",
        "ip": "172.42.0.11"
    }
}
```