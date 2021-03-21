from ansible.module_utils.basic import AnsibleModule
import os
import sys
import string

def generate_password(length):
    chars = string.ascii_letters + string.digits
    if sys.version_info.major == 3:
        return "".join(chars[c % len(chars)] for c in os.urandom(length))
    else:
        return "".join(chars[ord(c) % len(chars)] for c in os.urandom(length))


def main():
    module = AnsibleModule(
        argument_spec = dict(
            path   = dict(required=True, type='path'),
            state  = dict(default='present', choices=['present', 'absent']),
            length = dict(required=False, default=16, type="int"),
            set_fact = dict(required=False, type='str', default="")
            # mode: 600
            # owner: root
        )
    )

    changed = None

    path = module.params['path']
    length = module.params['length']
    password = None

    if module.params['state'] == 'present':
        if os.path.isfile(path):
            changed = False
            with open(path, "rt") as f:
                password = f.read().replace("\n", "")
        else:
            changed = True
            password = generate_password(length)

            dirname = os.path.dirname(path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            
            with open(path, "wt") as f:
                f.write("%s\n" % password)

    elif module.params['state'] == 'absent':
        if os.path.isfile(path):
            changed = True
            os.unlink(path)
        else:
            changed = False

    else:
        raise module.fail_json(msg='parameter "state": unknown value')

    if changed is None:
        raise module.fail_json(msg='bug: no changed value was set')

    facts = dict()
    if module.params['set_fact']:
        facts[module.params['set_fact']] = password

    module.exit_json(
        changed=changed,
        ansible_facts=facts
        )

if __name__ == '__main__':
    main()
