# Copyright 2024, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
#
# The back-end configuration.
terraform {
  #
  # Terraform Cloud is used here, for now...
  cloud {
    organization = "pvj1"

    workspaces {
      name = "pvj-vpn"
    }
  }
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "~>2.9.11"
    }
  }
}
