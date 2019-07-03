# -*- mode: ruby -*-
# vi: set ft=ruby :
require File.dirname(__FILE__)+"/vagrant/dependency_manager"

check_plugins ["vagrant-hosts"]

mysql_password = "A1a2a_"

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  nfs_ip = "192.168.10.5"

  config.vm.define "data" do |config|
    config.vm.box = "centos/7"
    #config.vm.network "forwarded_port", guest: 80, host: 8000
    #config.vm.hostname = vmName
    config.vm.network "private_network", ip: nfs_ip
  end

    app_ips = [
    "192.168.10.31",
    "192.168.10.32"
  ]

  app_ips.each_with_index do |app_ip, n|
    vmName = "app#{n + 1}"
    config.vm.define vmName do |config|
      config.vm.box = "centos/7"
      config.vm.hostname = vmName
      config.vm.network "private_network", ip: app_ip

      # Share an additional folder to the guest VM. The first argument is
      # the path on the host to the actual folder. The second argument is
      # the path on the guest to mount the folder. And the optional third
      # argument is a set of non-required options.
      config.vm.synced_folder '.', '/vagrant', disable: true
      config.vm.synced_folder '.',
                              '/var/phenome-10k/www',
                              mount_options: ["gid=1234"],
                              type: "rsync",
                              rsync__args:["-avz", "--rsync-path='sudo rsync'"]
    end
  end

  [1, 2].each do |n|
    vmName = "lb#{n}"
    config.vm.define vmName do |config|
      config.vm.box = "centos/7"
      #config.vm.network "forwarded_port", guest: 80, host: 8000
      #config.vm.hostname = vmName
      config.vm.network "private_network", ip: "192.168.10.1#{n}"
    end
  end

  config.vm.provision :hosts, :sync_hosts => true
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
    ansible.groups = {
      "app" => ["app1", "app2"],
      "lb" => ["lb1", "lb2"],
      "all:vars" => {
        "nfs_server" => nfs_ip,
        "app_servers" => ["app1", "app2"]
      }
    }
    ansible.host_vars = {
      "lb1" => {
        "vrrp_state" => "MASTER"
      },
      "lb2" => {
        "vrrp_state" => "BACKUP"
      }
    }
  end
end
