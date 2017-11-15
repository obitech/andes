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
# TODO: throw out
RESTART_FLAG=on-failure:3
HOSTNAME=localhost
ANDES_DIR=/home/$USER/andes
COMPOSE_VERSION=1.16.1
EMAIL=
CA_STAGING=true
# TODO: Enable caddy setup
CADDY_SETUP=false

echo -e "$GREEN---- Andes bootstrap script. Execute with -h to see options. $NC"

usage() {
  echo "Usage:
    $ bash bootstrap.sh [OPTIONS]
  
  Options:
    -h                     Display this help.
    -H <hostname>          Specify hostname for caddy to be reached under. Defaults to localhost
    -e <email>             Your email address needed for TLS certificates. If omitted, Caddy will run without TLS
    -d <directory>         Specify directory for Andes to be installed in. Defaults to /home/$USER/andes
    -V <version>           Docker-compose version. Defaults to 1.16.1
    -r                     Caddy container will always be restarted. Will set '--restart always' flag (Default: --restart on-failure:3)
    -c                     Set default CA to Let's Encrypt's staging cert. Use this for testing! Will only work with TLS enabled"

}

while getopts ":hrcH:d:V:e:" o; do
  case "${o}" in
    h )
      usage
      exit 0
      ;;
    H )
      IP=${OPTARG}
      ;;
    d )
      DIR=${OPTARG}
      ;;
    V )
      CV=${OPTARG}
      ;;
    e )
      EM=${OPTARG}
      ;;
    r )
      RESTART_FLAG=always
      ;;
    c )
      CA_STAGING=true
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

# TODO: Assign port, check w/ regex

# Check if passed directory exists
if [[ -n $DIR && -d $DIR ]]; then
  ANDES_DIR=$DIR/andes
elif [[ -z $DIR ]]; then
  DIR=$ANDES_DIR
else
  echo -e "$RED==> Error: Specified directory '$DIR' doesn't exist. $NC" 1>&2
  usage
  exit 1
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
CA_STAGING=$CA_STAGING
RESTART_FLAG=$RESTART_FLAG"
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

# TODO: Give possibility to install andes in different folder
echo -e "$GREEN==> Changing user permissions on $ANDES_DIR... $NC"
sudo chown $USER:$USER -R ./andes

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

#####################################################################
############################ CADDY SETUP ############################
#####################################################################
# TODO: Just bring up docker-compose
if [[ CADDY_SETUP ]]; then
  echo -e "$GREEN==> Creating Caddyfile in $ANDES_DIR/andes/system:$NC"
  if $TLS_ENABLED ; then
  echo "import 
    $HOSTNAME {
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
    - $ANDES_DIR/system/Caddyfile:/etc/caddy/Caddyfile
    - $ANDES_DIR/system/vhosts:/etc/caddy/sites-enabled
    - $ANDES_DIR/system/certs:/home/root/.caddy
    - $ANDES_DIR/system/www:/srv/www
  Restart:
    - $RESTART_FLAG $NC"

  # TODO: Variable for CA, default/live
  #  --ca https://acme-staging.api.letsencrypt.org/directory
  # default: https://acme-staging.api.letsencrypt.org/directory (staging)
  # live: custom
  if [[ TLS_ENABLED && CA_STAGING ]]; then
    sudo docker run \
      --name caddy \
      -p 80:80 \
      -p 443:443 \
      -p 2015:2015 \
      -v "$ANDES_DIR/system/Caddyfile:/etc/caddy/Caddyfile" \
      -v "$ANDES_DIR/system/vhosts:/etc/caddy/sites-enabled" \
      -v "$ANDES_DIR/system/certs:/home/root/.caddy" \
      -v "$ANDES_DIR/system/www:/srv/www" \
      --restart=$RESTART_FLAG \
      -d \
      abiosoft/caddy \
      --conf /etc/caddy/Caddyfile \
      --ca https://acme-staging.api.letsencrypt.org/directory
  else
    sudo docker run \
      --name caddy \
      -p 80:80 \
      -p 443:443 \
      -p 2015:2015 \
      -v "$ANDES_DIR/system/Caddyfile:/etc/caddy/Caddyfile" \
      -v "$ANDES_DIR/system/vhosts:/etc/caddy/sites-enabled" \
      -v "$ANDES_DIR/system/certs:/home/root/.caddy" \
      -v "$ANDES_DIR/system/www:/srv/www" \
      --restart=$RESTART_FLAG \
      -d \
      abiosoft/caddy \
      --conf /etc/caddy/Caddyfile
  fi

  echo
  echo -e "$GREEN==> Installation successful! Caddy is now running under $HOSTNAME:2015. You should logout and login again.$NC"
fi