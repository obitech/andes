# POST /stacks/<_id>/create
Applies a stack, generates a `docker-compose.yml` and saves it to disc in `andes/andes/stacks/<stack_name>`
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
201|Stack|Stack has been applied successfully.

## Example
### Request
`POST /stacks/1/apply`

### Response body
```json
{
    "status": 200,
    "message": "Stack foo_stack has been applied.",
    "error": null,
    "data": null
}
```