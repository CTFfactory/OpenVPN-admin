# Copyright 2023, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
provider "proxmox" {
  pm_tls_insecure     = true
  pm_api_url          = var.PM_API_URL # Proxmox API URL
  pm_api_token_id     = var.PM_API_TOKEN_ID
  pm_api_token_secret = var.PM_API_TOKEN_SECRET
  pm_debug            = true
}
