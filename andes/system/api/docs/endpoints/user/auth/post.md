# POST /auth
Authenticates a user and returns a JWT token.

## Headers
* `Content-Type: application/json`

## Body
Key | JSON Value type | Comment | Required
---|---|---
username|String|The username to be authenticated|Yes
password|String|The password of the user|Yes

## Returns
Status code | Data | Comments 
---|---|---
200|null|User created successfully.
400|null|Username already exists.

## Example
### Request
`POST /auth`
### Request body
```json
{
    "username": "foo",
    "password": "bar"
}
```
### Response body
```json
{
    "status": 201,
    "message": "User foo has been created.",
    "error": null,
    "data": null
}
```