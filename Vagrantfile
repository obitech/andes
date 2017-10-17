# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.define :andes_dev, primary: true do |andes_dev_config|
    config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
      vb.name = "andes_dev"
    end

    config.vm.provision "shell", inline: <<-SHELL
      apt-get update -y
      apt-get upgrade -y
      apt-get install vim curl git build-essential -y

      echo "Copying bootstrap.sh to /home/vagrant"
      cp /vagrant/bootstrap.sh /home/vagrant/
    SHELL
  end
end
