# DELETE /stacks/<_id>/apply
Deletes or purges a stack's project files. This will check if any service containers are running first and won't proceed if they are.

* Delete will remove the `docker-compose.yml` and `.conf` file
* Purge will also delete the project folder under `andes/stacks/<stack_name>`

## Headers
* `Authorization: JWT <JWT Token>`
* `Content-Type: application/json` (optional)

## Body
Key | JSON Value type | Comment | Required
---|---|---|---
purge|String|Can be true or false. If set to true, The project folder `andes/stacks/<stack_name>` will also be removed|No

## Returns
Status code | Data | Comments 
---|---|---
201|Null|Project files have been deleted.

## Example
### Request
`DELETE /stacks/1/apply?purge=true`

### Response body
```json
{
    "status": 201,
    "message": "Project files for stack foo_stack have been successfully removed.",
    "error": null,
    "data": null
}
```