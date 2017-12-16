# DELETE /blueprints/<_id>
Deletes a specific blueprint according to passed ID.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|null|Deletion of Blueprint successful.
400|null|Blueprint not found.

## Example
### Request
`DELETE /blueprints/1`
### Response body
```json
{
    "status": 200,
    "message": "Blueprint foo has been deleted.",
    "error": null,
    "data": null
}
```
