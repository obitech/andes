# DELETE /stacks/<_id>/manage/remove
Removes the containers for a specific stack. Will force remove if containers are still running.

## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|Null|Containers have been succsessfully removed

## Example
### Request
`DELETE /stacks/1/manage/down`
### Response body
```json
{
    "status": 200,
    "message": "Container for stack foo_stack have been removed successfully.",
    "error": null,
    "data": null
}
```