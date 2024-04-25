# Copyright 2022, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
resource "random_password" "password" {
  count       = length(local.teams)
  length      = 32
  special     = false
  min_numeric = 1
  min_upper   = 1
  min_lower   = 1
}

resource "local_file" "ansible_deploy" {
  content = templatefile("${path.module}/templates/ansible-deploy.tpl",
    {
      roles = [ openvpn ]
    }
  )
  filename = "deploy.yml"
}
