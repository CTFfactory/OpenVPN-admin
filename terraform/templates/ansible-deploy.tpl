---
%{ for role in roles ~}
- hosts:
  - ${role}
  gather_facts: no
  become: true
  roles:
  - ${role}
%{ endfor ~}
