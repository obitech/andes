# DELETE /stacks/<_id>
Deletes a specific stack according to passed ID. This will fail, if any containers are still in running or exited status.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|null|Deletion of stack has been successful.
400|null|Stack with passed name has not been found.

## Example
### Request
`DELETE /stacks/1`
### Response body
```json
{
    "status": 200,
    "message": "Stack foo_stack has been deleted.",
    "error": null,
    "data": null
}
```
