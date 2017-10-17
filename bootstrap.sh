#!/bin/bash
# Andes bootstrap script
set -e
set -o pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "$GREEN---- Andes bootstrap script. Execute with -h to see options. $NC"
echo

usage() {
  echo "Usage:
    $ bash bootstrap.sh [OPTIONS]
  
  Options:
    -h                     Display this help.
    -i <hostname>          Specify hostname for caddy to be reached under. Defaults to localhost
    -p <port>              Specify port for caddy to be reached under. Defaults to 2015
    -e <email>             Your email address needed for TLS certificates. If omitted, Caddy will run without TLS
    -d <directory>         Specify directory for Andes to be installed in. Defaults to /home/$USER/andes
    -c <version>           Docker-compose version. Defaults to 1.16.1
    -s                     Caddy container will always be restarted. Will set '--restart always' flag"
}

TLS_ENABLED=false
RESTART_FLAG=no

while getopts ":i:d:c:e:hs" o; do
  case "${o}" in
    h )
      usage
      exit 0
      ;;
    i )
      IP=${OPTARG}
      ;;
    d )
      DIR=${OPTARG}
      ;;
    c )
      CV=${OPTARG}
      ;;
    e )
      EM=${OPTARG}
      ;;
    s )
      RESTART_FLAG=always
      ;;
    \? )
      echo "Unknown option -$OPTARG"
      usage
      exit 1
      ;;
    : )
      echo "Missing parameter for -$OPTARG"
      usage
      exit 1
      ;;
    * )
      echo "Unimplemented option -$OPTARG"
      usage
      exit 1
      ;;
  esac
done
shift $(($OPTIND - 1))

# Assign hostname
if [[ -z $IP ]]; then
  HOSTNAME=localhost
else
  HOSTNAME=$IP
fi

# TODO: Assign port


# Check if passed directory exists
if [[ -n $DIR && -d $DIR ]]; then
  ANDES_DIR=$DIR/andes
elif [[ -z $DIR ]]; then
  ANDES_DIR=/home/$USER/andes
else
  echo -e "$RED==> Error: specified directory '$DIR' doesn't exist. $NC" 1>&2
  usage
  exit 1
fi

# Check for passed docker-compose version
if [[ -n $CV ]]; then
  COMPOSE_VERSION=$CV
else
  COMPOSE_VERSION=1.16.1
fi

# Check if Email address is passed
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
  EMAIL=
else
  echo -e "$RED==> Error: specified email '$EM' is invalid. $NC" 1>&2
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
RESTART_ALWAYS=$RESTART_FLAG"
echo
read -p "Continue (y/n)? " choice
case "$choice" in 
  y|Y|yes|Yes ) 
    ;;
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

echo -e "$GREEN==> Setting up folder structure in $ANDES_DIR... $NC"
mkdir -p $ANDES_DIR/system/certs $ANDES_DIR/system/templates $ANDES_DIR/system/vhosts $ANDES_DIR/projects $ANDES_DIR/system/www
echo "Welcome to Andes" > $ANDES_DIR/system/www/index.html
sudo chown $USER:$USER -R $ANDES_DIR

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

echo -e "$GREEN==> Testing hello-world...$NC"
sudo docker run hello-world

echo -e "$GREEN==> Docker installed successfully, source .bashrc for bash-completion! $NC"

#####################################################################
############################ CADDY SETUP ############################
#####################################################################

echo -e "$GREEN==> Creating Caddyfile in $ANDES_DIR/andes/system:$NC"
if $TLS_ENABLED ; then
echo "$HOSTNAME:80 {
  tls $EMAIL
  root /srv/www
  log stdout
  errors stdout
}"  > $ANDES_DIR/system/Caddyfile
else
echo "$HOSTNAME {
  tls off
  root /srv/www
  log stdout
  errors stdout
}" > $ANDES_DIR/system/Caddyfile
fi
cat $ANDES_DIR/system/Caddyfile

echo -e "$GREEN==> Pulling Caddy container from abiosoft/caddy...$NC"
sudo docker pull abiosoft/caddy

echo -e "$GREEN==> Starting Caddy container with parameters...
Name:
  - caddy
Forwarding ports:
  - 80:80
  - 443:443
  - 2015:2015
Mounting volumes:
  - $ANDES_DIR/system/Caddyfile:/etc/Caddyfile
  - $ANDES_DIR/system/certs:/home/root/.caddy
  - $ANDES_DIR/system/www:/srv/www
Restart:
  - $RESTART_FLAG $NC"

sudo docker run \
  --name caddy \
  -p 80:80 \
  -p 443:443 \
  -p 2015:2015 \
  -v "$ANDES_DIR/system/Caddyfile:/etc/Caddyfile" \
  -v "$ANDES_DIR/system/certs:/home/root/.caddy" \
  -v "$ANDES_DIR/system/www:/srv/www" \
  --restart=$RESTART_FLAG \
  -d \
  abiosoft/caddy