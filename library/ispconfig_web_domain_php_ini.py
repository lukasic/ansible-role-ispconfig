from ansible.module_utils.basic import AnsibleModule
import os
import string
import pymysql
import io
import requests
import json

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_config(raw_data):
    if not raw_data:
        return {}
    
    raw_data = raw_data.split('\n')

    config = {}
    for row in raw_data:
        if not row:
            continue
        k, v = row.split('=', 1)
        k = k.strip()
        v = v.strip()
        config[k] = v

    return config

def serialize_config(config):
    rows = list()
    for k in config.keys():
        row = '{} = {}'.format(k, config[k])
        rows.append(row)
    return '\n'.join(rows)

class ISPConfigApi:
    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self, ispconfig_url):
        self.api_url = ispconfig_url + "/remote/json.php"

    def _r(self, fnc, params):
        url = self.api_url + "?" + fnc
        params['session_id'] = self.session_id
        print("API Request:", json.dumps(params))
        resp = requests.post(url, json=params, headers=self.headers, verify=False)
        data = resp.json()
        print("API Response:", json.dumps(data))
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

    def get_domain_id(self, domain):
        params = {
            'session_id': self.session_id,
            'domain': domain
        }
        return self._r('sites_domain_get_id_by_name', params)

    def get_domain_id(self, domain):
        params = {
            'session_id': self.session_id,
            'domain': domain
        }
        return self._r('sites_domain_get_id_by_name', params)

    def domain_exists(self, domain):
        return self.get_domain_id(domain) != None

    def web_domain_get_param(self, domain, param):
        params = {
            'server_id': 1,
            'primary_id': self.get_domain_id(domain)
        }
        return self._r('sites_web_domain_get', params)[param]

    def web_domain_get(self, domain):
        params = {
            'server_id': 1,
            'primary_id': self.get_domain_id(domain)
        }
        return self._r('sites_web_domain_get', params)

    def web_domain_update_param(self, domain, param, value):
        params = {
            'client_id': 1,
            'primary_id': self.get_domain_id(domain),
            'params': {
                param: value
            }
        }
        self._r('sites_web_domain_update', params) 

def main():
    module = AnsibleModule(
        argument_spec = dict(
            api_url = dict(type='str', default='https://localhost:7777/'),
            api_user = dict(type='str', default='admin'),
            api_pass = dict(required=True, type='str'),
            domain = dict(required=True, type="str"),
            option = dict(required=True, type='str'),
            value = dict(type='str', default="")
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
    if not api.domain_exists(domain):
        raise RuntimeError("Site %s does not exists" % domain)

    raw_ini = api.web_domain_get_param(domain, 'custom_php_ini')
    config = parse_config(raw_ini)

    option = module.params['option'].strip()
    value = module.params['value'].strip()
    #replace("\'", '\\\'').replace("\"", "\\\"")

    if option in config.keys() and config[option] == value:
        module.exit_json(changed=False)

    config[option] = value
 
    raw_ini = serialize_config(config)
    api.web_domain_update_param(domain, 'custom_php_ini', raw_ini)

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
