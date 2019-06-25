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
  config.vm.define :data do |dockerConf|
    dockerConf.vm.provider "docker" do |d|
      d.image = "mysql"
      d.env = {
        MYSQL_ROOT_PASSWORD: mysql_password
      }
      d.ports = ['3306:3306']
    end
    dockerConf.vm.network :forwarded_port, guest: 3306, host: 3306

    dockerConf.trigger.after :up do |trigger|
      trigger.name = 'Allow connection from any host'
      trigger.run = { inline: "./vagrant/data.sh -h127.0.0.1 -uroot -p#{mysql_password}" }
    end
  end

  nfs_ip = "192.168.10.5"

  config.vm.define "files" do |config|
    config.vm.box = "centos/7"
    #config.vm.network "forwarded_port", guest: 80, host: 8000
    #config.vm.hostname = vmName
    config.vm.network "private_network", ip: nfs_ip
    config.vm.provision :hosts, :sync_hosts => true
  end

  [1, 2].each do |n|
    vmName = "lb#{n}"
    config.vm.define vmName do |config|
      config.vm.box = "centos/7"
      #config.vm.network "forwarded_port", guest: 80, host: 8000
      #config.vm.hostname = vmName
      config.vm.network "private_network", ip: "192.168.10.1#{n}"
      config.vm.provision :hosts, :sync_hosts => true
    end
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
      config.vm.provision :hosts, :sync_hosts => true

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

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
    ansible.groups = {
      "app" => ["app1", "app2"],
      "lb" => ["lb1", "lb2"],
      "app:vars" => {
        "p10k_db_url" => "mysql+pymysql://root:#{mysql_password}@10.0.2.2:3306/phenome10k",
        "nfs_server" => nfs_ip
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
