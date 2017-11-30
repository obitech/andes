# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  ubuntu = "bento/ubuntu-16.04"
  debian = "bento/debian-9.1"

  config.vm.box = "#{ubuntu}"

  # Mapping ports so we can access the frontend on our host machine
  config.vm.network "private_network", ip: "192.168.70.10"

  # VirtualBox settings
  config.vm.define :andes_dev, primary: true do |andes_dev_config|
    andes_dev_config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
      vb.name = "andes_dev"
    end
  end
end
