# POST /stacks/<_id>/manage/down
Shuts down a running stack. This basically applies a `docker-compose down` in the specific project folder `andes/stacks/<stack_name>`. The STDOUT for the command will be passed to the data field.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|String of STDOUT|Stack has been stopped successfully.

## Example
### Request
`POST /stacks/1/manage/down`
### Response body
```json
{
    "status": 200,
    "message": "Stack foo_stack has been shut down.",
    "error": null,
    "data": {
        "stdout": "Stopping foo_stack_foo_service ... \r\n\u001b[1A\u001b[2K\rStopping foo_stack_foo_service ... \u001b[32mdone\u001b[0m\r\u001b[1BRemoving foo_stack_foo_service ... \r\n\u001b[1A\u001b[2K\rRemoving foo_stack_foo_service ... \u001b[32mdone\u001b[0m\r\u001b[1BNetwork andes_default is external, skipping\n"
    }
}
```