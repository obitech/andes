# POST /stacks/<_id>/create
Applies a stack: 

* generates a `docker-compose.yml` and saves it to disc in `andes/andes/stacks/<stack_name>/docker-compose.yml`
* generates a `<stack_name>.conf` and saves it to dics in `andes/andes/stacks/conf.d/<stack_name>.conf`

The main Caddyfile will then import all `.conf` files in the `conf.d/` folder.

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

### Example stack used
```json
"data": {
    "id": 1,
    "name": "foo_stack",
    "description": "test stack",
    "subdomain": "test.example.com",
    "email": "test@example.com",
    "proxy_service": 1,
    "proxy_port": 80,
    "services": [1],
    "created_at": "2017-12-14T09:21:50.503274",
    "last_changed": "2017-12-14T09:21:50.503274"
}
```

### Example proxy_service used
```json
"data": {
    "id": 1,
    "blueprint": 1,
    "name": "foo_service",
    "description": "A test service",
    "stacks": [1],
    "exposed_ports": [80,8080],
    "mapped_ports": ["80:80"],
    "volumes": ["/srv/www:/"],
    "env": ["FOO=BAR","DEBUG=1"],
    "restart": "always",
    "ip": "172.42.0.11"
}
```

### Created .conf file
```
# Location: andes/stacks/conf.d/<foo_stack class="conf"></foo_stack>

test.example.com {
  test@example.com
  proxy / foo_service:80 {
    transparent
  }
  logs stdout
  errors stderror
}
```

### Create docker-compose.yml
```yaml
# Location: andes/stacks/foo_stack/docker-compose.yml

version: '3'
services:
  foo_service:
    image: abiosoft/caddy
    container_name: foo_stack_foo_service
    expose:
      - "80"
      - "8080"
    ports:
      - "80:80"
    volumes:
      - "/srv/www:/"
    environment:
      - "FOO=BAR"
      - "DEBUG=1"
    external_links:
      - caddy
    networks:
      andes_default:
        ipv4_address: 172.42.0.11
    restart: always
networks:
  andes_default:
    external: true
```