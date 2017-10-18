# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  ubuntu = "bento/ubuntu-16.04"
  debian = "bento/debian-9.1"

  config.vm.box = "#{ubuntu}"

  config.vm.define :andes_dev, primary: true do |andes_dev_config|
    config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
      vb.name = "andes_dev"
    end

  # Mapping ports so we can access the frontend on our host machine
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 4433
  config.vm.network "forwarded_port", guest: 2015, host: 2015

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update -y
    apt-get upgrade -y
    apt-get install vim curl git build-essential -y

    echo "Copying bootstrap.sh from /vagrant to /home/vagrant"
    cp /vagrant/bootstrap.sh /home/vagrant/
  SHELL
  end
end
