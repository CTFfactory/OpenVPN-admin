# Copyright 2024, luftegrof at duck dot com
#
# Licensed under GPL Version 3
# See LICENSE file for info.
#
output "roles" {
  value = [
      { hyphen : "common", underscore : "common" },
      { hyphen : "openvpn", underscore : "openvpn" }
    ]
}

output "role_names" {
  value = [
      "common",
      "openvpn"
    ]
}
