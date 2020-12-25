Ansible ISPConfig Role
======================

Ansible role for managing ISPConfig3 single host server.

Only for webserver and mailserver ISPConfig role.

Do not use in production. Role is under development.

Installation
------------

Using `ansible-galaxy`:

```bash
$ ansible-galaxy install lukasic.ispconfig
```

Using `requirements.yml`:

```yaml
- src: lukasic.ispconfig
```

Requirements
------------

Debian Buster.

Role Variables
--------------

TODO

Dependencies
------------

  - lukasic.php
  - lukasic.mariadb

Example Playbook
----------------

TODO

License
-------

WTFPL

Author Information
------------------

The role was created in 2020 by [Lukáš Kasič](https://github.com/lukasic).
