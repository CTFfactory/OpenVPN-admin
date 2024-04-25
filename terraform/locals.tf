# Copyright 2024, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
#
locals {
  #
  # Site-specific configuration...
  #
  #
  # Proxmox Cluster Information
  #
  # Proxmox Cluster Details used to place VMs in the right "buckets."
  pm_nodes = ["pvj-i-1", "pvj-i-2", "pvj-i-3", "pvj-i-4", "pvj-i-5"]
  #
  # High-Availability Groups
  #   https://pve.proxmox.com/wiki/High_Availability
  pm_ha_groups = ["i-1-plus", "i-2-plus", "i-3-plus", "i-4-plus", "i-5-plus"]
  pm_cpu       = "Westmere"
  #
  # Default VM Storage
  #
  pm_vm_storage = "VMs"
  #
  # VM Templates
  ubuntu_22_04_template = "ubuntu-server-22.04-template-202210171508"
  ubuntu_18_04_template = "ubuntu-server-18.04-template-202402290203"
  #
  # External infrastructure (DNS, NTP, etc...)
  name_servers = ["1.1.1.1", "9.9.9.9"]
  ntp_servers  = ["0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org"]
  log_server   = "169.254.1.1"

  site = "prosversusjoes"
  env = "net"

  openvpn = [ "vpn.prosversusjoes.net" ]
}
