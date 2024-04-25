# Copyright 2022, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#

data "local_file" "authorized_keys" {
  filename = "${path.module}/authorized_keys"
}
