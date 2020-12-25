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
            php_version = dict(required=True, type="str")
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
    sql = 'SELECT name FROM server_php WHERE name = "PHP %s"' % module.params['php_version']
    cursor.execute(sql)
    if len(cursor.fetchall()) > 0:
        module.exit_json(changed=False)

    sql = """
        INSERT INTO `server_php` (`sys_userid`, `sys_groupid`, `sys_perm_user`, `sys_perm_group`, `sys_perm_other`, `server_id`, `client_id`, `name`, `php_fastcgi_binary`, `php_fastcgi_ini_dir`, `php_fpm_init_script`, `php_fpm_ini_dir`, `php_fpm_pool_dir`)
        VALUES
            (1, 1, 'riud', 'riud', '', 1, 1, 'PHP {php_version}', NULL, NULL, '/etc/init.d/php{php_version}-fpm', '/etc/php/{php_version}/fpm/php.ini', '/etc/php/{php_version}/fpm/pool.d');
    """.format(php_version=module.params['php_version'])
    cursor.execute(sql)
    c.commit()

    cursor.close()
    c.close()

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
