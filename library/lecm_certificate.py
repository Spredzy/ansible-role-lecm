#!/usr/bin/python
#coding: utf-8 -*-
# Copyright 2016 Yanis Guenane <yguenane@redhat.com>
# Author: Yanis Guenane <yguenane@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from ansible.module_utils.basic import *

try:
    import yaml
except ImportError:
    pyyaml_found = False
else:
    pyyaml_found = True


_PROPERTIES = ['type', 'size', 'digest', 'version', 'subjectAltName',
               'countryName', 'stateOrProvinceName', 'localityName',
               'organizationName', 'organizationUnitName', 'commonName',
               'emailAddress', 'account_key_name', 'path', 'remaining_days',
               'service_name']


DOCUMENTATION = '''
---
module: lecm_certificate
short_description: An Ansible module to manage lecm certificates in the configuration file
version_added: 2.2
options:
  state:
    required: false
    choices: ['present', 'absent']
    default: 'present'
    description: Wheter or not the mode should be present
  config:
    required: false
    description: Path of the lecm config file, if not using the default
  name:
    required: true
    description: Name of the global parameter
  path:
    required: true
    description: Path to the git repository on the local filesystem
'''

EXAMPLES = '''
- name: Create a SSL certificate
  lecm_certificate: config=/etc/lecm.conf
                    name=lecm.example.com


- name: Remove a SSL certificate
  lecm_certificate: config=/etc/lecm.conf
                    name=lecm.example.com
                    state=absent
'''

RETURN = '''
name:
  description: Name of the SSL certificate
  type: string
  sample: lecm.example.com
path:
  description: Path to the git project
  type: string
  sample: /srv/git/git_superproject
'''

class Certificate(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.config = module.params['config']
        self.name = module.params['name']
        self.changed = True

        self.type = module.params['type']
        self.size = module.params['size']
        self.digest = module.params['digest']
        self.version = module.params['version']
        self.subjectAltName = module.params['subjectAltName']
        self.countryName = module.params['countryName']
        self.stateOrProvinceName = module.params['stateOrProvinceName']
        self.localityName = module.params['localityName']
        self.organizationName = module.params['organizationName']
        self.organizationUnitName = module.params['organizationUnitName']
        self.commonName = module.params['commonName']
        self.emailAddress = module.params['emailAddress']
        self.account_key_name = module.params['account_key_name']
        self.remaining_days = module.params['remaining_days']
        self.service_name = module.params['service_name']
        self.path = module.params['path']


    def write(self):
        l_certificate = {}
        for prop in _PROPERTIES:
            if getattr(self, prop):
                l_certificate[prop] = getattr(self, prop)

        try:
            lecm_conf = yaml.load(open(self.config, 'r'))
        except:
            lecm_conf = {}

        if lecm_conf is None:
            lecm_conf = {}

        certificates = {}
        c_certificate = None
        try:
            current_certificates = copy.deepcopy(lecm_conf['certificates'])
            for certificate, parameters in current_certificates.iteritems():
                if 'name' in parameters:
                    certificate_name = parameters['name']
                else:
                    certificate_name = certificate
                if certificate_name != self.name:
                    certificates[certificate_name] = parameters
                else:
                    c_certificate = parameters
        except KeyError:
            pass

        if c_certificate == l_certificate: 
            self.changed = False
        else:
            certificates[self.name] = l_certificate
            lecm_conf['certificates'] = copy.deepcopy(certificates)
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(lecm_conf))


    def remove(self):
        # Not Implemented yet
        pass

    def dump(self):
    
        result = {
          'name': self.name,
          'changed': self.changed,
        }

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            config=dict(required=False, type='path', default='/etc/lecm.conf'),
            name=dict(type='str'),

            type=dict(required=False, type='str'),
            size=dict(required=False, default='4096', type='str'),
            digest=dict(required=False, default='sha256', type='str'),
            version=dict(required=False, default='3', type='str'),
            subjectAltName=dict(required=False, type='str'),
            countryName=dict(required=False, type='str'),
            stateOrProvinceName=dict(required=False, type='str'),
            localityName=dict(required=False, type='str'),
            organizationName=dict(required=False, type='str'),
            organizationUnitName=dict(required=False, type='str'),
            commonName=dict(required=False, type='str'),
            emailAddress=dict(required=False, type='str'),
            account_key_name=dict(required=False, type='str'),
            path=dict(required=False, type='path'),
            remaining_days=dict(required=False, default='10', type='str'),
            service_name=dict(required=False, type='str'),
        ),
    )

    if not pyyaml_found:
        module.fail_json(msg='the python PyYAML module is required')

    path = module.params['config']
    base_dir = os.path.dirname(module.params['config'])

    if not os.path.isdir(base_dir):
        module.fail_json(name=base_dir, msg='The directory %s does not exist or the file is not a directory' % base_dir)

    certificate = Certificate(module)

    if certificate.state == 'present':
        certificate.write()
    else:
        certificate.remove()

    result = certificate.dump()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
