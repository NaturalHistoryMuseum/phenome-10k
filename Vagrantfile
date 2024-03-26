# -*- mode: ruby -*-
# vi: set ft=ruby :
require File.dirname(__FILE__)+"/vagrant/dependency_manager"

check_plugins ["vagrant-hosts", "vagrant-vbguest"]

mysql_password = "A1a2a_"

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  data_ip = "192.168.10.5"

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.define "data" do |config|
    config.vm.box = "generic/ubuntu2204"
    config.vm.network "private_network", ip: data_ip
    config.vbguest.no_install = true
  end

    app_ips = [
    "192.168.10.31",
    "192.168.10.32"
  ]

  app_ips.each_with_index do |app_ip, n|
    vmName = "app#{n + 1}"
    config.vm.define vmName do |config|
      config.vm.box = "generic/ubuntu2204"
      config.vm.hostname = vmName
      config.vm.network "private_network", ip: app_ip

      # Share an additional folder to the guest VM. The first argument is
      # the path on the host to the actual folder. The second argument is
      # the path on the guest to mount the folder. And the optional third
      # argument is a set of non-required options.
      config.vm.synced_folder '.', '/vagrant', disabled: true
      config.vm.synced_folder '.',
                              '/var/phenome-10k/www',
                              mount_options: ["gid=1234"]
    end
  end

  lb_ips = [
    "192.168.10.11",
    "192.168.10.12"
  ]

  lb_ips.each_with_index do |lb_ip, n|
    vmName = "lb#{n + 1}"
    config.vm.define vmName do |config|
      config.vm.box = "generic/ubuntu2204"
      config.vm.network "private_network", ip: lb_ip
      config.vbguest.no_install = true
    end
  end

  config.vm.provision :hosts, :sync_hosts => true
  config.vm.provision "ansible" do |ansible|
    ansible.compatibility_mode = "2.0"
    ansible.playbook = "ansible/playbook.yml"
    ansible.groups = {
      "app" => ["app1", "app2"],
      "lb" => ["lb1", "lb2"],
      "all:vars" => {
        "data_server" => data_ip,
        "app_servers" => app_ips,
        "lb_servers" => lb_ips
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
#     ansible.skip_tags = []
#     ansible.tags = []
  end
end
