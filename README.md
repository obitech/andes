# Andes
[![Docker Build Status](https://img.shields.io/docker/build/obitech/andes.svg)](https://hub.docker.com/r/obitech/andes/builds/) [![Docker Pulls](https://img.shields.io/docker/pulls/obitech/andes.svg)](https://hub.docker.com/r/obitech/andes/)

Andes is a self-hosted management tool for creating and deploying simple container "stacks" on a single host, reachable under a specific subdomain and with full TLS encryption powered by Let's Encrypt. Similiar to [Traefik](https://traefik.io) it allows multiple container environments to be reachable through a single webserver acting as reverse proxy, in this case [Caddy](https://caddyserver.com).

* [Documentation](https://obitech.github.io/andes/)

Please be aware that this project is still under development. Functionality is limited, things might not happen as expected or just break. 

## Getting started
### Using Vagrant
For this you will need [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed.

#### Clone the repo
```
git clone https://github.com/obitech/andes.git
cd andes/
```
#### Start Vagrant
```
vagrant up
vagrant ssh
```
#### Run the bootstrap script
Inside your virtual machine do:

```
cd /vagrant/andes
bash bootstrap.sh
```
#### Acess andes
Vagrant set up your VM to run on a private network, so you can reach the frontend from your host on ``192.168.70.10`` and the api on ``192.168.70.10/api``. 

### Running locally
#### Clone the repo
```
git clone https://github.com/obitech/andes.git
``` 

#### Run the bootstrap script
```
cd andes/andes/system
bash bootstrap.sh
```

Verify with ``docker container ls`` if the Caddy and andes container are running. You can then access the frontend via ``localhost`` and the api via ``localhost/api``.

### Taking requests
All endpoints take JSON requests, you can use [Postman](https://www.getpostman.com/) or good old curl for testing. Check the documentation for a reference on the API endpoints.