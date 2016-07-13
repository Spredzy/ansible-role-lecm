# Ansible Role: lecm

Installs and configures `lecm` on a server.


## Requirements

No special requirements; note that this role requires root access, so either run it in a playbook with a global `become: yes`, or invoke the role in your playbook like:

    - hosts: database
      roles:
        - role: Spredzy.lecm
          become: yes

## Role Variables

This is the list of role variables. Examples are found below.

  * `lecm_crons`
  * `lecm_globals`
  * `lecm_certificates`


## Dependencies

None.

## Example Playbook

    - hosts: all-servers
      become: yes
      vars_files:
        - vars/main.yml
      roles:
        - { role: Spredzy.lecm }

*Inside `vars/main.yml`*:


    lecm_crons:
      daily:
        minute: 0
        hour: 2
        job: 'lecm --renew'

    lecm_globals:
      path:
        value: /etc/ssl/letsencrypt
      account_key_name:
        value: myhost.key
      emailAddress:
        value: auser@adomain.com

    lecm_certificates:
      lecm_test_1:
      lecm_test_2:
        subjectAltName:
          - lecm_test_2
          - lecm_test_3


## License

Apache 2.0

## Author Information

Yanis Guenane <yguenane@redhat.com>
