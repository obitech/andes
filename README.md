# Andes

The ``master`` branch is used for development, until I've implemented a Python Docker container, there are two ways to run it: locally or with Vagrant.

## Using Vagrant
For this you will need [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed.

### Setup the repo
```
git clone https://github.com/obitech/andes.git
cd andes/
```
### Start Vagrant
```
vagrant up
vagrant ssh
```
Inside the Vagrant machine, navigate into the folder:
```
cd ~/andes/andes/systems/app/code
```
### Start Flask
First open ``app.py`` and set ``app.run(host='0.0.0.0', port=5000, debug=True)``, then you can start the app with
```
python3.6 app.py
```
Andes will then be reachable inside your guest VM and on your host via ``127.0.0.1:50000``

## Running locally
For this you will need **Python 3.6** installed. Using virtualenv is recommended.

### Setup the repo
```
git clone https://github.com/obitech/andes.git
``` 

### Set up virtualenv

```
cd andes/andes/system/app/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
cd code/
python3.6 app.py
```

## Taking requests
All endpoints take JSON requests, you can use [Postman](https://www.getpostman.com/) or good old curl for testing.
