# GET /stacks/<_id>/manage/logs
Retrieves the logs of a specific stack. Will be posted in the data field of the response.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Logs of stack as list of strings|Logs have been retrieved successfully.

## Example
### Request
`GET /stacks/1/manage/logs`
### Response body
```json
{
    "status": 200,
    "message": "Data for services in stack foo_stack has been retrieved.",
    "error": null,
    "data": [
        {
            "id": "1847b5a7f5",
            "name": "foo_stack_foo_service",
            "logs": [
                "Activating privacy features... done.",
                "http://0.0.0.0:2015",
                "2017/12/28 14:59:07 http://0.0.0.0:2015"
            ]
        }
    ]
}
```