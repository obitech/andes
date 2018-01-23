# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  ubuntu = "bento/ubuntu-16.04"
  debian = "bento/debian-9.1"

  config.vm.define :andes_dev, primary: true do |andes_dev_config|
    andes_dev_config.vm.box = "#{ubuntu}"
    andes_dev_config.vm.network "private_network", ip: "192.168.70.10" 
    
    andes_dev_config.vm.provision "shell", inline: <<-SHELL
      echo "127.0.0.1 test.localhost" > /etc/hosts
      cd /home/vagrant
      git clone https://github.com/obitech/andes.git
      chown -R vagrant:vagrant andes
    SHELL

    # VirtualBox settings
    andes_dev_config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
      vb.name = "andes_dev"
    end
  end
end
