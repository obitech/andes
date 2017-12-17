# Andes API Documentation

Welcome to Andes' API documentation. For information on classes and functions themselves, please refer to the source for now.

* [Github repo](https://github.com/obitech/andes)
* [Docker image](https://hub.docker.com/r/obitech/andes/)

## General

Andes offers an easy-to-use way to deploy multiple different container setups (stacks) on the same host. For this there are three parts:

* [Caddy](https://gocaddy.com) acting as a reverse proxy handling requests to your different stacks.
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

Responses return, in general, a JSON object with metadata and (if applicable) the actual data or an error message in the following format:

```json
# Sample format
{
    "status": <status code>,
    "message": <...>,
    "error": <...>,
    "data": <...>
}

For more information on the response format, have a look at the endpoint reference.

```

### Authentication

If you're starting from scratch you need to create a user first:

```
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
```
# Endpoint
POST /auth

#Header
Content-Type: application/json

# Body
{
    "username": "foo",
    "password": "bar"
}
```

Which will return a JWT token:
```
{
  "access_token": superSecretToken
}
```

This needs to be included in following requests as a header:
```
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