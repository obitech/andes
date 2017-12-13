#!/bin/bash
# Andes bootstrap script
# TODO: Copyright + Maintainer

# TODO: echo function with quiet mode, pipe in tee

# TODO: Acknowledgements
set -e
set -o pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

TLS_ENABLED=false
HOSTNAME=localhost
ANDES_DIR=/home/$USER/andes
COMPOSE_VERSION=1.16.1
EMAIL=
DOCKER_SETUP=true
CADDY_SETUP=true

echo -e "$GREEN---- Andes bootstrap script. Execute with -h to see options. $NC"

usage() {
  echo "Usage:
    $ bash bootstrap.sh [OPTIONS]
  
  Options:
    -h                     Display this help
    -c                     Skip Caddy install
    -d                     Skip Docker install
    -H <hostname>          Specify hostname for caddy to be reached under. Defaults to localhost
    -e <email>             Your email address needed for TLS certificates. If omitted, Caddy will run without TLS
    -V <version>           Docker-compose version. Defaults to 1.16.1"

}

while getopts ":hdcH:V:e:" o; do
  case "${o}" in
    h )
      usage
      exit 0
      ;;
    H )
      IP=${OPTARG}
      ;;
    V )
      CV=${OPTARG}
      ;;
    e )
      EM=${OPTARG}
      ;;
    d )
      DOCKER_SETUP=false
      ;;
    c )
      CADDY_SETUP=false
      ;;
    \? )
      echo -e "$RED==> Error: Unknown option -$OPTARG $NC"
      usage
      exit 1
      ;;
    : )
      echo -e "$RED==> Error: Missing parameter for -$OPTARG $NC"
      usage
      exit 1
      ;;
    * )
      echo -e "$RED==> Error: Unimplemented option -$OPTARG $NC"
      usage
      exit 1
      ;;
  esac
done
shift $(($OPTIND - 1))

# Assign hostname
if [[ -n $IP ]]; then
  HOSTNAME=$IP
fi

# Check for passed docker-compose version
if [[ -n $CV ]]; then
  COMPOSE_VERSION=$CV
fi

# Check if Email address has been passed
if [[ -z $EM ]]; then
  echo "Email (-e) omitted. Without an Email Caddy will not use TLS on initial startup."
  echo "Enter your email now or leave empty to deactivate TLS on startup (you can manually change your Caddyfile later):"
  read EM
fi

# Set Email address
if [[ -n $EM && $EM =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$ ]]; then
  EMAIL=$EM
  TLS_ENABLED=true
elif [[ -z $EM ]]; then
  EM=$EMAIL
else
  echo -e "$RED==> Error: Email '$EM' is invalid. $NC" 1>&2
  usage
  exit 1
fi

# Confirm if values are right
echo -e "$GREEN==> Starting bootstrap script with the following parameters:$NC"
echo "ANDES_DIR=$ANDES_DIR
COMPOSE_VERSION=$COMPOSE_VERSION
HOSTNAME=$HOSTNAME
EMAIL=$EMAIL
TLS_ENABLED=$TLS_ENABLED
DOCKER_SETUP=$DOCKER_SETUP
CADDY_SETUP=$CADDY_SETUP"

echo

read -p "Continue (Y/n)? " choice
case "$choice" in 
  n|N|no|No )
    echo -e "$RED==> Aborting."
    exit 1
    ;; 
  * )
    ;;
esac
echo

#############################################################################
############################ DOCKER INSTALLATION ############################
#############################################################################

if [[ "$DOCKER_SETUP" = true ]]; then
  echo -e "$GREEN==> Removing deprecated Docker versions... $NC"
  sudo apt-get remove docker docker-engine docker.io -y || true

  echo -e "$GREEN==> Updating package index... $NC"
  sudo apt-get update -y

  echo -e "$GREEN==> Installing additional packages... $NC"
  sudo apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      software-properties-common \
      bash-completion

  echo -e "$GREEN==> Adding docker's official GPG key... $NC"
  curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg \
      | sudo apt-key add -

  # TODO: put in Variable
  echo -e "$GREEN==> Verifying fingerprint: 9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88... $NC"
  sudo apt-key fingerprint 0EBFCD88

  echo -e "$GREEN==> Adding docker repository... $NC"
  sudo add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
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

  echo -e "$GREEN==> Testing hello-world...$NC"
  sudo docker run hello-world

  echo -e "$GREEN==> Docker installed successfully, source .bashrc for bash-completion! $NC"
fi

echo -e "$GREEN==> Setting up docker network andes_default... $NC"
sudo docker network create --subnet 172.42.0.0/16 andes_default

#####################################################################
############################ CADDY SETUP ############################
#####################################################################
  
if [[ "$CADDY_SETUP" = true ]]; then
  
  # Changing hostname
  if [[ "$HOSTNAME" != "localhost" ]]; then
    sed -i "s/localhost/$HOSTNAME/g" ./system/Caddyfile
    echo -e "$GREEN==> Caddyfile: Hostname has been changed to $HOSTNAME. $NC"
  fi

  # Setting TLS
  # TODO: fix this
  if [[ "$EMAIL" ]]; then
    sed -i "s/tls off/tls $EMAIL/g" ./system/Caddyfile
    echo -e "$GREEN==> Caddy: tls Email has been changed to $EMAIL. $NC"
  fi

  echo -e "$GREEN==> Caddyfile has been saved:$NC"
  cat ./system/Caddyfile

  read -p "Do you want to start Andes now (Y/n)? " choice
  case "$choice" in 
    n|N|no|No )
      echo -e "$RED==> Aborting."
      exit 1
      ;; 
    * )
      ;;
  esac

  echo -e "$GREEN==> Starting Andes...$NC"
  sudo docker-compose up -d

  echo
  echo -e "$GREEN==> Installation successful! Caddy is now running under $HOSTNAME:2015. You should logout and login again.$NC"
fi