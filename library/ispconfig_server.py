# https://github.com/Uberspace/ansible-mountopts

from ansible.module_utils.basic import AnsibleModule
import os
import string
import pymysql
import io
import configparser

def main():
    module = AnsibleModule(
        argument_spec = dict(
            mysql_dbname = dict(type='str', default='_dbispconfig'),
            mysql_user  = dict(type='str', default='_ispconfig'),
            mysql_pass  = dict(required=True, type='str', no_log=True),
            server = dict(required=True, type="str"),
            ini_group = dict(required=True, type="str"),
            ini_option = dict(required=True, type='str'),
            ini_value = dict(type='str', default="")
        )
    )

    c = pymysql.connect(
        host='localhost',
        user=module.params['mysql_user'],
        password=module.params['mysql_pass'],
        db=module.params['mysql_dbname'],
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = c.cursor()
    sql = 'SELECT config FROM server WHERE server_name = "%s"' % module.params['server']
    cursor.execute(sql)
    raw_ini = cursor.fetchone()['config']

    ini = configparser.ConfigParser()
    ini.read_string(raw_ini)

    changed = False

    ini_group = module.params['ini_group']
    ini_option = module.params['ini_option']
    ini_value = module.params['ini_value']

    try:
        current_value = ini[ini_group][ini_option]
    except:
        current_value = None

    if current_value != ini_value:
        changed = True
        ini[ini_group][ini_option] = ini_value

        stream = io.StringIO()
        ini.write(stream, space_around_delimiters=False)
        raw_ini = stream.getvalue().replace("\'", '\\\'').replace("\"", "\\\"")
        sql = 'UPDATE server SET config = "%s" WHERE server_name = "%s"' % (raw_ini, module.params['server'])
        cursor.execute(sql)
        c.commit()

    cursor.close()
    c.close()
 
    if changed is None:
        raise module.fail_json(msg='bug: no changed value was set')

    module.exit_json(changed=changed)

if __name__ == '__main__':
    main()
