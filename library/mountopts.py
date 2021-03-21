from ansible.module_utils.basic import AnsibleModule
import os.path


class Line:
    ATTRS = ( "device", "path", "fs", "options", "dump", "fsck" )

    def __init__(self, raw):
        self.raw = raw
        self.attrs = None
        self.parse()
    
    def parse(self):
        self.has_mount = False
        
        if not self.raw.strip():
            return
        
        if self.raw.strip()[0] == '#':
            return

        tokens = self.raw.strip().split()
        if len(tokens) != len(self.ATTRS):
            return
        
        self.attrs = dict(zip(self.ATTRS, tokens))
        self.has_mount = True

    def get_options(self):
        return self.attrs['options'].split(',')

    def set_options(self, opts):
        self.attrs['options'] = ','.join(opts)
    
    def __str__(self):
        if self.has_mount:
            return '\t'.join([self.attrs[i] for i in self.ATTRS])
        else:
            return self.raw


class Fstab:
    def __init__(self, path="/etc/fstab"):
        self.path = path
        self.lines = []
        self.read()
    
    def read(self):
        self.lines = []
        with open(self.path, "r") as f:
            data = f.read().split('\n')
        
        for r in data:
            l = Line(r)
            self.lines.append(l)
    
    def save(self):
        data = '\n'.join([str(l) for l in self.lines])
        with open(self.path, "w") as f:
            f.write(data)


def find_mount(ft, path):
    for l in ft.lines:
        if l.has_mount and l.attrs['path'] == path:
            return l


def parse_options(options):
    parsed = {}

    for opt in options:
        if '=' in opt:
            opt = opt.split('=')
            parsed[opt[0]] = opt[1]
        else:
            parsed[opt] = None

    return parsed


def dump_options(options):
    dumped = []

    for opt, val in options.items():
        if val is None:
            dumped.append(opt)
        else:
            dumped.append("{}={}".format(opt, val))

    return dumped


def main():
    module = AnsibleModule(
        argument_spec = dict(
            fstab  = dict(default='/etc/fstab', type='path'),
            name   = dict(required=True, type='path'),
            state  = dict(default='present', choices=['present', 'absent']),
            option = dict(required=True),
            value  = dict(),
        )
    )

    if not os.path.exists(module.params['fstab']):
        module.fail_json(msg='fstab file does not exist: ' + module.params['fstab'])

    changed = None

    fst = Fstab(path=module.params['fstab'])

    line = find_mount(fst, module.params['name'])

    if not line:
        module.fail_json(msg='mountpoint does not exist: {}.'.format(module.params['name']))

    opts = parse_options(line.get_options())

    if module.params['state'] == 'present':
        if module.params['value']:
            changed = (opts.get(module.params['option'], None) != module.params['value'])
            opts[module.params['option']] = module.params['value']
        else:
            changed = (module.params['option'] not in opts)
            opts[module.params['option']] = None
    elif module.params['state'] == 'absent':
        if module.params['option'] in opts:
            del opts[module.params['option']]
            changed = True
        else:
            changed = False
    else:
        raise module.fail_json(msg='parameter "state": unknown value')

    line.set_options(dump_options(opts))
    fst.save()

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
