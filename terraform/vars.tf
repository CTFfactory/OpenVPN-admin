# Copyright 2023, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
variable "PM_API_URL" {
  type        = string
  description = "Proxmox API URL"
}
variable "PM_API_TOKEN_ID" {
  type        = string
  description = "Proxmox API TOKEN ID"
  sensitive   = true
}
variable "PM_API_TOKEN_SECRET" {
  type        = string
  description = "Proxmox API TOKEN SECRET"
  sensitive   = true
}
