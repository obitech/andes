#!/bin/bash
# Andes bootstrap script - run as root!
set -e
set -o pipefail

CWD=$(pwd)
ANDES_DIR=$CWD/andes
COMPOSE_VERSION=1.16.1

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "$GREEN==> Creating default folder structure in $CWD/andes... $NC"
mkdir -p $ANDES_DIR/system/certs $ANDES_DIR/system/templates $ANDES_DIR/system/vhosts $ANDES_DIR/projects
sudo chown $USER:$USER $CWD/andes

echo -e "$GREEN==> Removing deprecated Docker versions... $NC"
sudo apt-get remove docker docker-engine docker.io -y

echo -e "$GREEN==> Updating package index... $NC"
sudo apt-get update -y

echo -e "$GREEN==> Installing additional packages... $NC"
sudo apt-get install -y \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    bash-completion

echo -e "$GREEN==> Adding docker's official GPG key... $NC"
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg \
    | sudo apt-key add -

echo -e "$GREEN==> Verifying fingerprint: 9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88... $NC"
sudo apt-key fingerprint 0EBFCD88

echo -e "$GREEN==> Adding docker repository... $NC"
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

echo -e "$GREEN==> Updating package index... $NC"
sudo apt-get update -y

echo -e "$GREEN==> Installing docker from package manager... $NC"
sudo apt-get install docker-ce -y

echo -e "$GREEN==> Creating docker group and adding user '$USER'... $NC"
sudo groupadd docker || true
sudo usermod -aG docker $USER

echo -e "$GREEN==> Adding docker to systemd... $NC"
sudo systemctl enable docker

echo -e "$GREEN==> Downloading docker-compose $COMPOSE_VERSION... $NC"
sudo curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo -e "$GREEN==> Adding docker-compose to bash-completion...$NC"
sudo curl -L https://raw.githubusercontent.com/docker/compose/${COMPOSE_VERSION}/contrib/completion/bash/docker-compose -o /usr/share/bash-completion/completions/docker-compose

echo -e "$GREEN==> Docker installed successfully, relog to use bash-completion! $NC"