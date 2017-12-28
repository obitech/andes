# POST /stacks/<_id>/manage/up
Launches a stack. This basically applies a `docker-compose up -d` in the specific project folder `andes/stacks/<stack_name>`. Will fail if containers are already running. The STDOUT for the command will be passed to the data field.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|String of STDOUT|Stack has been started successfully.

## Example
### Request
`POST /stacks/1/manage/up`
### Response body
```json
{
    "status": 200,
    "message": "Stack foo_stack has been started.",
    "error": null,
    "data": {
        "stdout": "Creating foo_stack_foo_service ... \r\nCreating foo_stack_foo_service\n\u001b[1A\u001b[2K\rCreating foo_stack_foo_service ... \u001b[32mdone\u001b[0m\r\u001b[1B"
    }
}
```