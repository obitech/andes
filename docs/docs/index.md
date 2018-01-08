# Andes API Documentation

Welcome to Andes' API documentation. For information on classes and functions themselves, please refer to the source for now.

* [Github repo](https://github.com/obitech/andes)
* [Docker image](https://hub.docker.com/r/obitech/andes/)

## General

Andes offers an easy-to-use way to deploy multiple different container setups (stacks) on the same host. For this there are three parts:

* [Caddy](https://caddyserver.com) acting as a reverse proxy handling requests to your different stacks.
* Andes API to create and manage your stacks and build your docker-compose files.
* Docker-compose bringing up your previously defined stacks as docker-compose.yml files.

Normally the workflow looks like that:

1. You register a blueprint, which is essentially a docker image on docker hub, or one you created locally.
2. From a blueprint you create a service, which is defining your container environment
3. You add one or more services to a stack.
4. You apply a stack, which will create the `docker-compose.yml` and specific `Caddyfile` for it.
5. You launch your stack and Caddy will serve it on your specified subdomain.

Note that Andes' stacks have nothing to do with the `docker stack` command in swarm mode.

## Installation

After you've cloned the github repo, the best way to setup andes is to run the bootstrap script. This installation has been tested on Debian, Ubuntu and macOS.

### `bootstrap.sh`

The script accepts the following arguments:

Argument|Function
---|---
`-h`|Displays usage information
`-c`|Skips Caddy installation and setup. Use this flag if you only want to install docker and docker-compose
`-d`|Skips docker and docker-compose installation. Use this flag if you have already docker installed and just want to setup Caddy for Andes.
`-H <hostname>`|Specifies the hostname Caddy to be reached under. Defaults to localhost
`-e <email>`|Your email address which is required to setup Let's Encrypt TLS certificates. Without this, TLS can not be used.
`-V <version>`|The docker-compose version to be installed. Defaults to 1.17.1

#### Docker installation
For the docker installation, the script follows the procedure from the official docker documentation

1. Remove deprecated docker packages
2. Install additional packages, namely
    * `apt-transport-https`
    * `ca-certificates`
    * `curl`
    * `software-properties-common`
    * `bash-completion`
3. Add and verify docker's official GPG key
4. Add and install the `docker-ce` repository.
5. Add your user to the docker group
6. Enable the docker.service
7. Curl and install docker-compose, plus add it to `bash-completion`

Between the docker and Caddy setup, the script will also create a user defined docker network with subnet `172.42.0.0./16` where Caddy and the deployed containers will run in.

#### Caddy setup

1. Create a `Caddyfile` in `andes/andes/system` according to the previously passed arguments
2. Pull the [Caddy container image](https://hub.docker.com/r/abiosoft/caddy)
3. Pull the [Andes API container image](https://hub.docker.com/r/obitech/andes)
4. Bring up the `docker-compose.yml` in `andes/andes/system`.

Check with `docker container ls` if you have the andes and Caddy container up and running. The API will will be reachable under your specified hostname + `/api`

## Using the API
### Start & Stop

If you're installing andes from the bootstrap script, andes will launch afterwards. There are also convenience scripts in the `andes/andes` directory to start and stop the API:

Name|Translates to|Function
---|---|---
`start_andes.sh`|`docker-compose up -d`|Starts andes as daemonized process
`stop_andes.sh`|`docker-compose down`|Stops andes
`follow_logs.sh`|`docker-compose logs -f`|Streams andes logs to STDOUT. Exit with CTRL+C
`show_logs.sh`|`docker-compose logs`|Shows andes logs

## Response format
Responses return, in general, a JSON object with metadata and (if applicable) the actual data or an error message in the following format:

```json
# Sample format
{
    "status": <status code>,
    "message": <...>,
    "error": <...>,
    "data": <...>
}
```
For more information on the response format, have a look at the endpoint reference.

### Authentication

If you're starting from scratch you need to create a user first:

```json
# Endpoint
POST /register

# Header
Content-Type: application/json

# Body
{
    "username": "foo",
    "password": "bar"
}
```

Now you need to authenticate: 

```json
# Endpoint
POST /auth

# Header
Content-Type: application/json

# Body
{
    "username": "foo",
    "password": "bar"
}
```

Which will return a JWT token:

```json
{
  "access_token": superSecretToken
}
```

This needs to be included in following requests as a header:

```json
# Endpoint
GET /stacks

# Header
Authorization: JWT superSecretToken

# Response
{
    "status": 200,
    "message": "Stacks have been retrieved.",
    "error": null,
    "data": []
}
```

## Creating a new blueprint
Before we create a service, we have to create a blueprint first. This is essentially defining a Docker image, either built locally or from a registry. Please note that at this point there is no functionality to build the image with the andes API, or define a custom registry other than docker hub. If you want to change any of that, you will have to do it manually. 

Let's create a simple Caddy blueprint:

```json
# Endpoint
POST /blueprints/create

# Headers (will be omitted for brevity in future examples)
Content-Type: application/json
Authorization: JWT superSecretToken

# Body
{
	"name": "foo",
	"description": "bar",
	"image": "abiosoft/caddy"
}

# Response
{
    "status": 201,
    "message": "Blueprint foo has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo",
        "description": "bar",
        "image": "abiosoft/caddy",
        "services": []
    }
}
```

## Creating a new service
From this newly created blueprint we can start to define services and attach them to stacks. While a blueprint only defines an image, a service holds information about exposed ports, mapped volumes, environment variables, etc.

```json
# Endpoint
POST /services/create

# Body
{
	"name": "foo_service",
	"description": "A test service",
	"mapped_ports": ["81:80", "2015:2015"],
	"blueprint": 1
}

# Response
{
    "status": 201,
    "message": "Service foo_service has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "blueprint": 1,
        "name": "foo_service",
        "description": "A test service",
        "stacks": [],
        "exposed_ports": null,
        "mapped_ports": [
            "81:80",
            "2015:2015"
        ],
        "volumes": null,
        "env": null,
        "restart": null,
        "ip": "172.42.0.11"
    }
}
```

We can see here that the service has been created with [forwarded ports](https://docs.docker.com/compose/compose-file/#ports) defined and an IP automatically assigned.

## Creating a new stack

Next we use our created service and define it in a stack. You can define as many different services in a stack as you wish but for this example we will stick to just our newly created service.

```json
# Endpoint
POST /stacks/create

# Body
{
	"name": "foo_stack",
	"description": "test stack",
	"services": [1],
	"proxy_service": 1,
	"subdomain": "test.localhost",
	"proxy_port": 2015
}

# Response
{
    "status": 201,
    "message": "Stack foo_stack has been updated.",
    "error": null,
    "data": {
        "id": 1,
        "name": "foo_stack",
        "description": "test stack",
        "subdomain": "test.localhost",
        "email": null,
        "proxy_service": 1,
        "proxy_port": 2015,
        "services": [
            1
        ],
        "created_at": "2018-01-08T14:33:27.671960",
        "last_changed": "2018-01-08T14:33:27.671960"
    }
}

```

For the stack we have to define a service and a port to which our main Caddy will route the request to. In our case this is service 1 with port 2015. For demonstration purposes the subdomain will be test.localhost, you have to substitute this with your own domain. Also there is no email defined because in this case we're not using TLS encryption. If you want to use automatic TLS encryption, make sure to provide your email here.

## Starting our stack

Now that we have created our stack and saved it to the database, let's create the necessary config files in order to start the stack through docker-compose:

```json
# Endpoint
POST /stacks/1/apply

# Response
{
    "status": 200,
    "message": "Stack foo_stack has been applied.",
    "error": null,
    "data": null
}
```

If you look into your folder under `andes/andes/stacks` you will see two files:

### `stacks/conf.d/foo_stack.conf`
This file will be imported to our main Caddy with information about how to route traffic:

```
test.localhost {
  tls off
  proxy / foo_service:2015 {
    transparent
  }
  log stdout
  errors stderror
}
```

### `stacks/foo_stack/docker-compose.yml`
This file gets created from information in the stack with its specific services and will later be started with docker-compose:

```yaml
version: '3'
services:
  foo_service:
    image: abiosoft/caddy
    container_name: foo_stack_foo_service
    ports:
      - "81:80"
      - "2015:2015"
    external_links:
      - caddy
    networks:
      andes_default:
        ipv4_address: 172.42.0.11
networks:
  andes_default:
    external: true
```

With those files created we can safely launch our stack:

```json
# Endpoint
POST /stacks/1/manage/up

# Response
{
    "status": 200,
    "message": "Stack foo_stack has been started.",
    "error": null,
    "data": {
        "stdout": "Creating foo_stack_foo_service ... \r\nCreating foo_stack_foo_service\n\u001b[1A\u001b[2K\rCreating foo_stack_foo_service ... \u001b[32mdone\u001b[0m\r\u001b[1B"
    }
}
```

We can now check on our command line if our service is running:

```
$ docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                                 NAMES
80743ddc0038        abiosoft/caddy         "/usr/bin/caddy --..."   49 seconds ago      Up 49 seconds       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp, 2015/tcp    andes_web_1
28bc4189d7f4        obitech/andes:latest   "uwsgi uwsgi.ini"        50 seconds ago      Up 50 seconds       5000-5001/tcp                                         andes_andes_1
acc382a68636        abiosoft/caddy         "/usr/bin/caddy --..."   16 seconds ago      Up 16 seconds       443/tcp, 0.0.0.0:2015->2015/tcp, 0.0.0.0:81->80/tcp   foo_stack_foo_service
```

You can check via `test.localhost` (you might have to adjust your `/etc/hosts` beforehand) that your new service containing Caddy is indeed running and reachable.

