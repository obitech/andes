# Andes

The ``master`` branch is used for development, however you can already run it as a container.

## Using Vagrant
For this you will need [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed.

### Clone the repo
```
git clone https://github.com/obitech/andes.git
cd andes/
```
### Start Vagrant
```
vagrant up
vagrant ssh
```
### Run the bootstrap script
Inside your virtual machine do:

```
cd /vagrant/andes
bash bootstrap.sh
```
### Acess andes
The frontend will then be available via ``192.168.70.10`` and the api via ``192.168.70.10/api``

## Running locally
If you just want to try it out, do the following:

### Clone the repo
```
git clone https://github.com/obitech/andes.git
``` 

### Run the bootstrap script
```
cd andes/andes/system
bash bootstrap.sh
```

Verify with ``docker ps`` if the Caddy and andes container are running. You can then access the frontend via ``localhost`` and the api via ``localhost/api``.

## Taking requests
All endpoints take JSON requests, you can use [Postman](https://www.getpostman.com/) or good old curl for testing.
