from ansible.module_utils.basic import AnsibleModule
import os
import string
import pymysql
import io
import configparser
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ISPConfigApi:
    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self, ispconfig_url):
        self.api_url = ispconfig_url + "/remote/json.php"

    def _r(self, fnc, params):
        url = self.api_url + "?" + fnc
        params['session_id'] = self.session_id
        resp = requests.post(url, json=params, headers=self.headers, verify=False)
        data = resp.json()
        if data['code'] != 'ok':
            raise RuntimeError("API Error: " + data['message'])
        return data['response']

    def login(self, username, password):
        url = self.api_url + "?login"
        params = {
            'username': username,
            'password': password
        }
        resp = requests.post(url, json=params, headers=self.headers, verify=False).json()
        if resp['code'] != 'ok':
            raise RuntimeError('Invalid credentials')
        self.session_id = resp['response']

    def database_exists(self, database_name):
        params = {
            'session_id': self.session_id,
            'database_name': database_name
        }
        return self._r('sites_database_get_id_by_name', params) != None

    def get_domain_id(self, domain):
        params = {
            'session_id': self.session_id,
            'domain': domain
        }
        return self._r('sites_domain_get_id_by_name', params)

    def get_database_user_id(self, username):
        params = {
            'session_id': self.session_id,
            'username': username
        }
        return self._r('sites_database_user_get_id_by_name', params)

    def database_user_exists(self, username):
        return self.get_database_user_id(username) != None

    def database_user_add(self, username, password):
        params = {
            'server_id': 1,
            'database_user': username,
            'database_password': password
        }
        self._r('sites_database_user_add', params)

    def database_add(self, database_name, database_username, domain):
        user_id = self.get_database_user_id(database_username)
        domain_id = self.get_domain_id(domain)
        params = {
            'server_id': 1,
            'type': "mysql",
            'website_id': domain_id,
            'parent_domain_id': domain_id,
            'database_name': database_name,
            'database_user_id': user_id,
            'database_charset': 'utf8mb4',
            'remote_access': 'n',
            'active': 1
        }
        self._r('sites_database_add', params)

    def get_domain_id(self, domain):
        params = {
            'session_id': self.session_id,
            'domain': domain
        }
        return self._r('sites_domain_get_id_by_name', params)

    def domain_exists(self, domain):
        return self.get_domain_id(domain) != None

    def web_domain_add(self, domain):
        params = {
            'server_id': 1,
            'ip_address': "*",
            'domain': domain,
            'type': 'vhost',
            'parent_domain_id': 0,
            'vhost_type': 'name',
            'hd_quota': "-1",
            'traffic_quota': "-1",
            'cgi': 'n',
            'ssi': 'n',
            'suexec': 'y',
            'subdomain': 'none',
            'php': 'php-fpm',
            'ruby': 'n',
            'rewrite_to_https': 'y',
            'ssl': 'n',
            'ssl_letsencrypt': 'n',
            'stats_type': 'awstats',
            'allow_override': 'all',
            'active': 'y',
            'added_by': 'ansible',
            'http_port': "80",
            'https_port': "443",
            "pm": "dynamic",
            'php_fpm_use_socket': 'y',
            "pm_max_requests": "0",
            "pm_max_children": "10",
            "pm_min_spare_servers": "1",
            "pm_max_spare_servers": "5",
            "pm_start_servers": "2",
            "pm_process_idle_timeout": "10",
        }
        params = {
            'client_id': 1,
            'params': params
        }
        self._r('sites_web_domain_add', params)            


def main():
    module = AnsibleModule(
        argument_spec = dict(
            api_url = dict(type='str', default='https://localhost:7777/'),
            api_user = dict(type='str', default='admin'),
            api_pass = dict(required=True, type='str'),
            #
            domain = dict(required=True, type='str')
        )
    )

    api = ISPConfigApi(
        module.params['api_url']
        )
    api.login(
        module.params['api_user'],
        module.params['api_pass']
        )

    domain = module.params['domain']
    if api.domain_exists(domain):
        module.exit_json(changed=False)

    api.web_domain_add(domain)
    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
