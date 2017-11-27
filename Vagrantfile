# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  ubuntu = "bento/ubuntu-16.04"
  debian = "bento/debian-9.1"

  config.vm.box = "#{ubuntu}"

  # Mapping ports so we can access the frontend on our host machine
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 4433
  config.vm.network "forwarded_port", guest: 2015, host: 2015
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  # Provision script
  config.vm.provision "shell", inline: <<-SHELL
    add-apt-repository ppa:jonathonf/python-3.6 -y
    apt-get update -y
    apt-get upgrade -y
    # apt-get install vim python3.6 -y
    # curl https://bootstrap.pypa.io/get-pip.py | sudo python3.6
    # apt-get upgrade -y
    # pip3 install -r /home/vagrant/andes/andes/system/app/requirements.txt
  SHELL

  # Sync this folder to ~ inside VM and disable standard syncing
  # config.vm.synced_folder ".", "/vagrant", disabled: true
  # config.vm.synced_folder ".", "/home/vagrant/andes"

  # VirtualBox settings
  config.vm.define :andes_dev, primary: true do |andes_dev_config|
    andes_dev_config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
      vb.name = "andes_dev"
    end
  end
end
