# DELETE /services/<_id>
Deletes a specific service according to passed ID.
## Headers
* `Authorization: JWT <JWT Token>`

## Returns
Status code | Data | Comments 
---|---|---
200|null|Deletion of Service successful.
400|null|Service with passed name has not been found.

## Example
### Request
`DELETE /services/1`
### Response body
```json
{
    "status": 200,
    "message": "Service foo has been deleted.",
    "error": null,
    "data": null
}
```
