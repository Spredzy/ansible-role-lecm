#!/usr/bin/python
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

import os

from ansible.module_utils.basic import *

try:
    import yaml
except ImportError:
    pyyaml_found = False
else:
    pyyaml_found = True


DOCUMENTATION = '''
---
module: lecm_global
short_description: An Ansible module to manage lecm globals in the configuration file
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
  value:
    required: false
    description: Value of the global parameter
'''

EXAMPLES = '''
- name: Create a new global parameter
  lecm_global:
    config: /etc/lecm.conf
    name: remaining_days
    value: 10

- name: Remove a global parameter
  lecm_global:
    config: /etc/lecm.conf
    name: remaining_days
    ensure: absent
'''

RETURN = '''
name:
  description: Name of the global parameter
  type: string
  sample: remaining_days
value:
  description: Value of the global parameter
  type: string
  sample: True
'''


class Parameter(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.config = module.params['config']
        self.name = module.params['name']
        self.value = module.params['value']
        self.changed = True

    def write(self):
        try:
            lecm_conf = yaml.load(open(self.config, 'r'))
        except:
            lecm_conf = {}

        if lecm_conf is None:
            lecm_conf = {}

        try:
            if lecm_conf[self.name] == self.value:
                self.changed = False
        except KeyError:
            pass

        if self.changed:
            lecm_conf[self.name] = self.value
            with open(self.config, 'w') as conf_file:
                conf_file.write(
                    yaml.dump(
                        lecm_conf, explicit_start=True, default_flow_style=False
                    )
                )

    def remove(self):
        try:
            lecm_conf = yaml.load(open(self.config, 'r'))
        except:
            lecm_conf = {}

        if lecm_conf is None:
            lecm_conf = {}

        try:
            del lecm_conf[self.name]
            with open(self.config, 'w') as conf_file:
                conf_file.write(
                    yaml.dump(
                        lecm_conf, explicit_start=True, default_flow_style=False
                    )
                )

        except KeyError:
            self.changed = False

    def dump(self):
        result = {
          'name': self.name,
          'value': self.value,
          'changed': self.changed,
        }

        return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            config=dict(required=False, type='path', default='/etc/lecm.conf'),
            name=dict(type='str'),
            value=dict(required=False, type='str'),
        ),
    )

    if not pyyaml_found:
        module.fail_json(msg='the python PyYAML module is required')

    path = os.path.dirname(module.params['config'])
    if not os.path.isdir(path):
        module.fail_json(name=path, msg='Directory %s does not exist' % path)

    parameter = Parameter(module)

    if parameter.state == 'present':
        parameter.write()
    else:
        parameter.remove()

    result = parameter.dump()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
