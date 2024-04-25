# Copyright 2023, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#

module "openvpn" {
  source  = "app.terraform.io/pvj1/proxmox-linux/module"
  version = "~>1.0.0"
  #
  #  Inherited from local Environment variables.
  #    Be sure to run `pm_get_token` before running terraform.
  pm_host             = split(":", split("/", var.PM_API_URL)[2])[0] # Proxmox API Host         (run pm_get_token).
  pm_api_url          = var.PM_API_URL                               # Proxmox API URL          (run pm_get_token).
  pm_api_token_id     = var.PM_API_TOKEN_ID                          # Proxmox API token ID     (run pm_get_token).
  pm_api_token_secret = var.PM_API_TOKEN_SECRET                      # Proxmox API token secret (run pm_get_token).
  #
  #  Inherited from locals.tf.
  for_each = { for i, v in local.openvpn : i => v }
  # Temporarily set agents to same node as server until MTUs are increased on underlay switches.
  target_node = local.pm_nodes[each.key % length(local.pm_nodes)]         # Initial node on which the VM will build & run.
  hagroup     = local.pm_ha_groups[each.key % length(local.pm_ha_groups)] # Restrict range routers to one node only.
  hastate     = "started"
  #
  log_server = local.log_server
  #
  #  Set these parameters to your liking.
  name               = each.value
  desc               = "vpn.prosversusjoes.net"
  clone              = local.ubuntu_18_04_template                           # The desired template revision.
  cloud_init_storage = "ISOs"                                                # Location for the Clout-init seed ISOs.
  full_clone         = false                                                 # Full-clone = true, Linked-clone = false.
  boot               = "order=virtio0;net0;ide2"                             # Sometimes you need to specify the boot order.
  onboot             = true                                                  # Start this VM with the node?
  oncreate           = true                                                  # Start this VM when it is created?
  agent              = 1                                                     # 1 = qemu-agent running, 0 = no qemu-agent.
  pool               = infra # Proxmox resource pool
  cpu                = local.pm_cpu
  cores              = 4    # CPU cores.
  sockets            = 1    # CPU sockets.  vCPUs = (cores * sockets).
  memory             = 16384 # RAM in MB.
  qemu_os            = "l26"
  authorized_keys    = data.local_file.authorized_keys.content
  site               = local.site
  env                = local.env
  username           = "aureus"
  password           = length(resource.random_password.team_pass) > 0 ? resource.random_password.team_pass[0].result : ""
  interfaces = [
    {
      name   = "host",
      desc   = "Host Network",
      dev    = "eth0",
      mtu    = "1500",
      net    = "10.20.30.0",
      addr   = "10.20.30.112",
      cidr   = "24",
      gw     = "10.20.30.1",
      vlan   = 30,
      model  = "virtio",
      bridge = "vmbr0"
    },
    {
      name   = "vpn",
      desc   = "VPN Network",
      dev    = "eth1",
      mtu    = "1500",
      net    = "10.1.139.0",
      addr   = "10.1.139.10",
      cidr   = "26",
      gw     = "10.1.139.1",
      vlan   = 3
      model  = "virtio",
      bridge = "vmbr0"
    }
  ]
}

module "ansible_openvpn" {
  source    = "app.terraform.io/pvj1/ansible-inventory/module"
  version   = "~>1.0.0"
  inventory = module.openvpn
  group     = "openvpn"
  category  = "infra"
}
