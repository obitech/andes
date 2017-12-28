# GET /stacks/<_id>/manage/status
Retrieves status information about running or exited containers of the specific stack. Will fail if no containers are running or exited.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Status information of stack and running services|Info has been retrieved successfully.

## Example
### Request
`GET /stacks/1/manage/status`
### Response body
```json
{
    "status": 200,
    "message": "Data for services in stack foo_stack has been retrieved.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo_stack",
        "subdomain": "localhost",
        "port": 2015,
        "services": [
            {
                "id": "1847b5a7f5",
                "name": "foo_stack_foo_service",
                "status": "running",
                "labels": {
                    "caddy_version": "0.10.10",
                    "com.docker.compose.config-hash": "9b9eaac0e5419599dd382a6bab29a71ab4371bbdaa251d53de3de26543d93e12",
                    "com.docker.compose.container-number": "1",
                    "com.docker.compose.oneoff": "False",
                    "com.docker.compose.project": "foostack",
                    "com.docker.compose.service": "foo_service",
                    "com.docker.compose.version": "1.17.1",
                    "maintainer": "Abiola Ibrahim <abiola89@gmail.com>"
                }
            }
        ]
    }
}
```