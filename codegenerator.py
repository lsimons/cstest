# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# forked from marvin codegenerator.py

import xml.dom.minidom
import json
from optparse import OptionParser
from textwrap import dedent
import os
import urllib2
import re

from ezt import Template


_capital_re = re.compile('[A-Z]')
_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')

"""Commands that start with one of these verbs will be associated with a model."""
_recognized_command_verbs = ['activate', 'add', 'archive', 'assign', 'associate', 'attach', 'authorize', 'cancel',
                             'change', 'clean', 'configure', 'copy', 'create', 'dedicate', 'delete', 'deploy',
                             'destroy', 'detach', 'disable', 'disassociate', 'enable', 'expunge', 'extract',
                             # findHostsForMigration, findStoragePoolsForMigration
                             'generate', 'get',
                             'list', 'lock',
                             # login, logout,
                             # mark
                             'migrate', 'prepare',
                             # queryAsyncJobResult
                             'reboot', 'reconnect', 'recover', 'register', 'release', 'remove',
                             # replaceNetworkACLList
                             'reset', 'resize', 'restart', 'restore',
                             # revertSnapshot, revertToVMSnapshot
                             'revoke',
                             'scale', 'start', 'stop', 'suspend', 'update',
                             # upgradeRouterTemplate
                             'upload']


"""Commands with these names are associated with the specified model."""
_custom_cmd_to_model_mapping = {
    'markDefaultZoneForAccount': 'Account',

    'listAffinityGroupTypes': 'AffinityGroup',

    'login': 'Api',
    'logout': 'Api',
    'getApiLimit': 'Api',
    'resetApiLimit': 'Api',
    'getCloudIdentifier': 'Api',
    'updateCloudToUseObjectStore': 'Api',
    'uploadCustomCertificate': 'Api',
    'listDeploymentPlanners': 'Api',

    'listAsyncJobs': 'Async',
    'queryAsyncJobResult': 'Async',

    'removeCertFromLoadBalancer': 'LoadBalancer',
    'assignCertToLoadBalancer': 'LoadBalancer',
    'removeFromLoadBalancerRule': 'LoadBalancer',
    'listLoadBalancerRuleInstances': 'LoadBalancerRule',
    'assignToLoadBalancerRule' : 'LoadBalancer',
    'removeFromGlobalLoadBalancerRule': 'GlobalLoadBalancerRule',
    'assignToGlobalLoadBalancerRule' : 'GlobalLoadBalancerRule',
    'listNetscalerLoadBalancerNetworks': 'NetscalerLoadBalancer',

    'listDedicatedClusters': 'Cluster',
    'releaseDedicatedCluster': 'Cluster',

    'listDomainChildren': 'Domain',

    'listEventTypes': 'Event',

    'listOsCategories' : 'GuestOs',
    'listOsTypes' : 'GuestOs',

    'listDedicatedGuestVlanRanges': 'GuestVlanRange',
    'releaseDedicatedGuestVlanRange': 'GuestVlanRange',

    'listDedicatedHosts': 'Host',
    'releaseDedicatedHost': 'Host',
    'prepareHostForMaintenance': 'Host',
    'cancelHostMaintenance': 'Host',
    'updateHostPassword': 'Host',
    'releaseHostReservation': 'Host',
    'listHostTags': 'Host',
    'findHostsForMigration': 'Host',
    'findStoragePoolsForMigration': 'Host',

    'listHypervisorCapabilities' : 'Hypervisor',
    'updateHypervisorCapabilities' : 'Hypervisor',
    
    'removeIpFromNic': 'Nic',
    'addIpToNic': 'Nic',
    'removeNicFromVirtualMachine': 'Nic',
    'addNicToVirtualMachine': 'Nic',

    'disableStaticNat': 'IpAddress',
    'enableStaticNat': 'IpAddress',

    'listIsoPermissions': 'Iso',
    'updateIsoPermissions': 'Iso',

    'listNetworkIsolationMethods': 'Network',
    'listPublicIpAddresses': 'Network',
    'replaceNetworkACLList': 'Network',

    'updateNetworkACLItem': 'NetworkACL',

    'dedicatePublicIpRange': 'PublicIpRange',
    'releasePublicIpRange': 'PublicIpRange',

    'listDedicatedPods': 'Pod',
    'releaseDedicatedPod': 'Pod',

    'deleteAccountFromProject': 'Project',
    'addAccountToProject': 'Project',
    'listProjectAccounts': 'Project',

    'updateResourceCount': 'Resource',
    'addResourceDetail': 'Resource',
    'listResourceDetails': 'Resource',
    'removeResourceDetail': 'Resource',
    'listResourceLimits': 'Resource',
    'updateResourceLimit': 'Resource',

    'changeServiceForRouter': 'Router',
    'upgradeRouterTemplate': 'Router',

    'changeServiceForSystemVm': 'SystemVm',

    'createTags': 'Tag',
    'deleteTags': 'Tag',

    'listTemplatePermissions' : 'Template',
    'updateTemplatePermissions' : 'Template',

    'listTrafficTypeImplementors' : 'TrafficType',

    'listUsageRecords' : 'UsageRecord',
    'generateUsageRecords' : 'UsageRecord',
    'listUsageTypes' : 'UsageRecord',

    'registerUserKeys' : 'User',

    'listDedicatedZones': 'Zone',
    'releaseDedicatedZone': 'Zone',

    'updateDefaultNicForVirtualMachine': 'VirtualMachine',
    'resetSSHKeyForVirtualMachine': 'VirtualMachine',
    'resetPasswordForVirtualMachine': 'VirtualMachine',
    'getVMPassword' : 'VirtualMachine',
    'cleanVMReservations' : 'VirtualMachine',
    'getVirtualMachineUserData' : 'VirtualMachine',
    'migrateVirtualMachineWithVolume' : 'VirtualMachine',
    'updateVMAffinityGroup': 'VirtualMachine',
    'changeServiceForVirtualMachine': 'VirtualMachine',

    'revertSnapshot': 'VMSnapshot',
    'revertToVMSnapshot': 'VMSnapshot',


    'importLdapUsers': 'Ldap',
    'ldapCreateAccount': 'Ldap',
    'listLdapUsers': 'Ldap',

    'getSPMetadata': 'Saml',
    'samlSlo': 'Saml',
    'samlSso': 'Saml',

    'addBaremetalDhcp': 'Baremetal',
    'listBaremetalDhcp': 'Baremetal',
    'addBaremetalHost': 'Baremetal',
    'addBaremetalPxeKickStartServer': 'Baremetal',
    'addBaremetalPxePingServer': 'Baremetal',
    'listBaremetalPxeServers': 'Baremetal',

    'listBrocadeVcsDeviceNetworks': 'BrocadeVcsDevice',

    'createServiceInstance': 'Contrail',

    'addGloboDnsHost': 'GloboDns',

    'listNiciraNvpDeviceNetworks': 'NiciraNvpDevice',

    'listPaloAltoFirewallNetworks': 'PaloAltoFirewall',

    'getSolidFireAccountId': 'SolidFire',
    'getSolidFireVolumeAccessGroupId': 'SolidFire',
    'getSolidFireVolumeIscsiName': 'SolidFire',
    'getSolidFireVolumeSize': 'SolidFire',
    
    'listUcsBlades' : 'Ucs',
    'addUcsManager' : 'Ucs',
    'listUcsManagers' : 'Ucs',
    'listUcsProfiles' : 'Ucs',
    'associateUcsProfileToBlade' : 'Ucs',
        
}


class CmdParameterProperty(object):
    def __init__(self):
        self.name = None
        self.required = False
        self.desc = ""
        self.type = "planObject"
        self.subProperties = []
        self._dataType = ""
        self.pythonType = ""
    
    @property
    def dataType(self):
        return self._dataType
    
    @dataType.setter
    def dataType(self, dataType):
        self._dataType = dataType
        if dataType == "string":
            self.pythonType = "basestring"
        elif dataType == "integer":
            self.pythonType = "int"
        elif dataType == "boolean":
            self.pythonType = "bool"
        elif dataType == "[]":
            self.pythonType = "list"
        elif dataType == "date":
            self.pythonType = "basestring"
            self.desc += " (string format of a date)"
        elif dataType == "short":
            self.pythonType = "int"
        elif dataType == "map":
            self.pythonType = "dict"
        elif dataType == "list":
            self.pythonType = "list"
        elif dataType is not None:
            self.pythonType = dataType


class CloudStackCmd(object):
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.async = "false"
        """:type: list[CmdParameterProperty]"""
        self.request_params = []
        """:type: list[CmdParameterProperty]"""
        self.response_params = []


class CodeGenerator(object):
    space = '    '
    newline = '\n'
    cmdsName = []

    def __init__(self, outputFolder):
        self.cmd = None
        self.code = ""
        self.required = []
        self.subclass = []
        self.outputFolder = outputFolder
        lic = """# Licensed to the Apache Software Foundation (ASF) under one
          # or more contributor license agreements.  See the NOTICE file
          # distributed with this work for additional information
          # regarding copyright ownership.  The ASF licenses this file
          # to you under the Apache License, Version 2.0 (the
          # "License"); you may not use this file except in compliance
          # with the License.  You may obtain a copy of the License at
          #
          #   http://www.apache.org/licenses/LICENSE-2.0
          #
          # Unless required by applicable law or agreed to in writing,
          # software distributed under the License is distributed on an
          # "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
          # KIND, either express or implied.  See the License for the
          # specific language governing permissions and limitations
          # under the License.

          """
        self.license = dedent(lic)

    def add_attribute(self, attr, pro):
        value = pro.value
        if pro.required:
            self.required.append(attr)
        desc = pro.desc
        if desc is not None:
            self.code += self.space
            self.code += '""" ' + pro.desc + ' """'
            self.code += self.newline

        self.code += self.space
        self.code += attr + " = " + str(value)
        self.code += self.newline

    def generate_sub_class(self, name, properties):
        subclass = 'class %s:\n' % name
        subclass += self.space + "def __init__(self):\n"
        for pro in properties:
            if pro.desc is not None:
                subclass += self.space + self.space + '""""%s"""\n' % pro.desc
            if len(pro.subProperties) > 0:
                subclass += self.space + self.space
                subclass += 'self.%s = []\n' % pro.name
                self.generate_sub_class(pro.name, pro.subProperties)
            else:
                subclass += self.space + self.space
                subclass += 'self.%s = None\n' % pro.name

        self.subclass.append(subclass)

    def generate_command(self, cmd):
        self.cmd = cmd
        self.cmdsName.append(self.cmd.name)
        self.code = self.license
        self.code += self.newline
        self.code += '"""%s"""\n' % self.cmd.desc
        self.code += 'from baseCmd import *\n'
        self.code += 'from baseResponse import *\n'
        self.code += "class %sCmd (baseCmd):\n" % self.cmd.name
        self.code += self.space
        self.code += 'typeInfo = {}\n'
        self.code += self.space + "def __init__(self):\n"

        self.code += self.space + self.space
        self.code += 'self.isAsync = "%s"\n' % str(self.cmd.async).lower()

        for req in self.cmd.request:
            if req.desc is not None:
                self.code += self.space + self.space + '"""%s"""\n' % req.desc
            if req.required == "true":
                self.code += self.space + self.space + '"""Required"""\n'

            value = "None"
            if req.type == "list" or req.type == "map":
                value = "[]"

            self.code += self.space + self.space
            self.code += 'self.%s = %s\n' % (req.name, value)
            if req.required == "true":
                self.required.append(req.name)
            self.code += self.space + self.space
            self.code += "self.typeInfo['%s'] = '%s'\n" % ( req.name, req.dataType )

        self.code += self.space + self.space + "self.required = ["
        for require in self.required:
            self.code += '"' + require + '",'
        self.code += "]\n"
        self.required = []

        self.code += self.newline
        self.code += 'class %sResponse (baseResponse):\n' % self.cmd.name
        self.code += self.space
        self.code += 'typeInfo = {}\n'
        self.code += self.space + "def __init__(self):\n"
        if len(self.cmd.response) == 0:
            self.code += self.space + self.space + "pass"
        else:
            for res in self.cmd.response:
                if res.desc is not None:
                    self.code += self.space + self.space
                    self.code += '"""%s"""\n' % res.desc

                if len(res.subProperties) > 0:
                    self.code += self.space + self.space
                    self.code += 'self.%s = []\n' % res.name
                    self.generate_sub_class(res.name, res.subProperties)
                else:
                    self.code += self.space + self.space
                    self.code += 'self.%s = None\n' % res.name
                    if res.dataType is not None:
                        self.code += self.space + self.space
                        self.code += "self.typeInfo['%s'] = '%s'\n" % ( res.name, res.dataType )

        self.code += self.newline

        for subclass in self.subclass:
            self.code += subclass + "\n"

        fp = open(self.outputFolder + "/csapi/%s.py" % self.cmd.name, "w")
        fp.write(self.code)
        fp.close()
        self.code = ""
        self.subclass = []

    def finalize(self):
        header = '"""Test Client for CloudStack API"""\n'
        imports = "import copy\n"
        initCmdsList = '__all__ = ['
        body = ''
        body += "class CloudStackAPIClient(object):\n"
        body += self.space + 'def __init__(self, connection):\n'
        body += self.space + self.space + 'self.connection = connection\n'
        body += self.space + self.space + 'self._id = None\n'
        body += self.newline

        body += self.space + 'def __copy__(self):\n'
        body += self.space + self.space
        body += 'return CloudStackAPIClient(copy.copy(self.connection))\n'
        body += self.newline

        # The `id` property will be used to link the test with the cloud
        # resource being created
        #            @property
        #            def id(self):
        #                return self._id
        #
        #            @id.setter
        #            def id(self, identifier):
        #                self._id = identifier

        body += self.space + '@property' + self.newline
        body += self.space + 'def id(self):' + self.newline
        body += self.space * 2 + 'return self._id' + self.newline
        body += self.newline

        body += self.space + '@id.setter' + self.newline
        body += self.space + 'def id(self, identifier):' + self.newline
        body += self.space * 2 + 'self._id = identifier' + self.newline
        body += self.newline

        for cmdName in self.cmdsName:
            body += self.space
            body += 'def %s(self, command, method="GET"):\n' % cmdName
            body += self.space + self.space
            body += 'response = %sResponse()\n' % cmdName
            body += self.space + self.space
            body += 'response = self.connection.marvinRequest(command,'
            body += ' response_type=response, method=method)\n'
            body += self.space + self.space + 'return response\n'
            body += self.newline

            imports += 'from %s import %sResponse\n' % (cmdName, cmdName)
            initCmdsList += '"%s",' % cmdName

        fp = open(self.outputFolder + '/csapi/csapiClient.py',
                  'w')
        fp.write(self.license)
        for item in [header, imports, body]:
            fp.write(item)
        fp.close()

        initCmdsList = self.license + initCmdsList + '"cloudstackAPIClient"]'
        fp = open(self.outputFolder + '/csapi/__init__.py', 'w')
        fp.write(initCmdsList)
        fp.close()

        fp = open(self.outputFolder + '/csapi/base.py', 'w')
        basecmd = self.license
        basecmd += '"""Base Command"""\n'
        basecmd += 'class BaseCmd(object):\n'
        basecmd += self.space + 'pass\n'
        basecmd += self.newline
        basecmd += self.newline
        basecmd += '"""Base class for response"""\n'
        basecmd += 'class baseResponse(object):\n'
        basecmd += self.space + 'pass\n'
        fp.write(basecmd)
        fp.close()

    @staticmethod
    def to_camel_case(model_name):
        s1 = _first_cap_re.sub(r'\1_\2', model_name)
        return _all_cap_re.sub(r'\1_\2', s1).lower()
    
    def generate_model(self, model_name='model', **kwargs):
        template = './templates/%s.tpl' % model_name
        if not os.path.exists(template):
            template = './templates/model.tpl'
        template = Template(fname=template, compress_whitespace=0)
        data = dict(kwargs)
        data['model_name'] = model_name
        model_file = self.outputFolder + '/csapi/model/' + self.to_camel_case(model_name) + ".py"
        with open(model_file, 'w') as f:
            template.generate(f, data)

    def generate_api(self, model_name='model', **kwargs):
        template = './templates/%s_api.tpl' % model_name
        if not os.path.exists(template):
            template = './templates/api.tpl'
        template = Template(fname=template, compress_whitespace=0)
        data = dict(kwargs)
        data['model_name'] = model_name
        data['package_name'] = self.to_camel_case(model_name)
        data['variable_name'] = self.to_camel_case(model_name)
        model_file = self.outputFolder + '/csapi/' + self.to_camel_case(model_name) + ".py"
        with open(model_file, 'w') as f:
            template.generate(f, data)

    @staticmethod
    def method_name(command_name):
        if command_name.startswith("update"):
            pass
        match = _capital_re.search(command_name)
        if match:
            first_word = command_name[0:match.start()]
        else:
            first_word = None

        if first_word in _recognized_command_verbs:
            return first_word, True
        else:
            return command_name, False

    @staticmethod
    def model_name(command_name):
        match = _capital_re.search(command_name)
        if match:
            noun = command_name[match.start():]
        else:
            raise Exception('method_name matched, but model_name didn\'t')
        return noun

    def extract_models(self, cmds):
        """
        :type cmds: list[CloudStackCmd]
        :returns dict[str, dict[str, CloudStackCmd]]
        """
        models = {}
        commands = {}
        for cmd in cmds:
            command_belongs_to_model = True
            method_name = cmd.name
            if cmd.name in _custom_cmd_to_model_mapping:
                model_name = _custom_cmd_to_model_mapping[cmd.name]
            else:
                method_name, recognized_verb = self.method_name(cmd.name)
                if recognized_verb:
                    model_name = self.model_name(cmd.name)
                    if model_name.endswith('ies'):
                        model_name = model_name[:-3] + 'y'
                    elif method_name == 'list' and model_name.endswith('s'):
                        model_name = model_name[:-1]
                else:
                    command_belongs_to_model = False

            if command_belongs_to_model:
                if not model_name in models:
                    models[model_name] = {}
                if method_name in models[model_name]:
                    raise Exception('Want to put %s as %s on %s but %s is already there' % (
                        cmd.name, method_name, model_name, models[model_name][method_name].name))
                models[model_name][method_name] = cmd
            else:
                commands[cmd.name] = cmd
        if len(commands) > 0:
            raise Exception("Don't know model for commands: %s" % ",".join(commands.keys()))
        return models

    @staticmethod
    def extract_fields(methods):
        field_names = []
        fields = []
        for model_method_name in ["create", "update"]:
            if not model_method_name in methods:
                continue
            method = methods[model_method_name]
            assert isinstance(method, CloudStackCmd)
            for p in method.response_params:
                if not p.name in field_names:
                    field_names.append(p.name)
                    fields.append(p)
            for p in method.request_params:
                if not p.name in field_names:
                    field_names.append(p.name)
                    fields.append(p)
        return fields

    def generate(self, cmds):
        """
        :type cmds: list[CloudStackCmd]
        """
        models = self.extract_models(cmds)
            
        model_names = models.keys()
        model_names.sort()
        for model_name in model_names:
            print "MODEL:", model_name
            methods = models[model_name]
            method_names = methods.keys()
            method_names.sort()
            for method_name in method_names:
                print "    " + method_name + " -> " + methods[method_name].name

            fields = self.extract_fields(methods)
            self.generate_model(model_name=model_name, methods=methods, fields=fields)
            self.generate_api(model_name=model_name, methods=methods, fields=fields)


class XmlCodeGenerator(CodeGenerator):
    def construct_response(self, response):
        paramProperty = CmdParameterProperty()
        paramProperty.name = get_text(response.getElementsByTagName('name'))
        paramProperty.desc = get_text(response.getElementsByTagName('description'))
        dataType = response.getElementsByTagName('dataType')
        if dataType:
            paramProperty.dataType = get_text(dataType)
        if paramProperty.name.find('(*)') != -1:
            paramProperty.name = paramProperty.name.split('(*)')[0]
            argList = response.getElementsByTagName('arguments')[0].getElementsByTagName('arg')
            for subresponse in argList:
                subProperty = self.construct_response(subresponse)
                paramProperty.subProperties.append(subProperty)
        return paramProperty

    def load_command(self, cmd):
        csCmd = CloudStackCmd()
        csCmd.name = get_text(cmd.getElementsByTagName('name'))
        assert csCmd.name
        desc = get_text(cmd.getElementsByTagName('description'))
        if desc:
            csCmd.desc = desc
        async = get_text(cmd.getElementsByTagName('isAsync'))
        if async:
            csCmd.async = async
        argList = cmd.getElementsByTagName("request")[0].getElementsByTagName("arg")
        for param in argList:
            paramProperty = CmdParameterProperty()
            paramProperty.name = get_text(param.getElementsByTagName('name'))
            assert paramProperty.name

            required = param.getElementsByTagName('required')
            if required:
                paramProperty.required = get_text(required)
            requestDescription = param.getElementsByTagName('description')
            if requestDescription:
                paramProperty.desc = get_text(requestDescription)
            paramType = param.getElementsByTagName("type")
            if paramType:
                paramProperty.type = get_text(paramType)
            dataType = param.getElementsByTagName('dataType')
            if dataType:
                paramProperty.dataType = get_text(dataType)

            csCmd.request_params.append(paramProperty)
        responseEle = cmd.getElementsByTagName("response")[0]
        for response in responseEle.getElementsByTagName("arg"):
            if response.parentNode != responseEle:
                continue

            paramProperty = self.construct_response(response)
            csCmd.response_params.append(paramProperty)
        return csCmd

    def load_commands(self, dom):
        cmds = []
        for cmd in dom.getElementsByTagName("command"):
            csCmd = self.load_command(cmd)
            cmds.append(csCmd)
        return cmds

    def generate_from_file(self, specFile):
        dom = xml.dom.minidom.parse(specFile)
        cmds = self.load_commands(dom)
        self.generate(cmds)

class JsonCodeGenerator(CodeGenerator):
    def construct_response(self, response):
        paramProperty = CmdParameterProperty()
        if 'name' in response:
            paramProperty.name = response['name']
        assert paramProperty.name, "%s has no property name" % response

        if 'description' in response:
            paramProperty.desc = response['description']
        if 'type' in response:
            if response['type'] in ['list', 'map', 'set']:
                # Here list becomes a subproperty
                if 'response' in response:
                    for innerResponse in response['response']:
                        subProperty = self.construct_response(innerResponse)
                        paramProperty.subProperties.append(subProperty)
            paramProperty.type = response['type']
        return paramProperty

    def load_command(self, cmd):
        csCmd = CloudStackCmd()
        if 'name' in cmd:
            csCmd.name = cmd['name']
        assert csCmd.name
        if 'description' in cmd:
            csCmd.desc = cmd['description']
        if 'isasync' in cmd:
            csCmd.async = cmd['isasync']
        for param in cmd['params']:
            paramProperty = CmdParameterProperty()
            if 'name' in param:
                paramProperty.name = param['name']
            assert paramProperty.name
            if 'required' in param:
                paramProperty.required = param['required']
            if 'description' in param:
                paramProperty.desc = param['description']
            if 'type' in param:
                paramProperty.type = param['type']
            csCmd.request_params.append(paramProperty)
        for response in cmd['response']:
            # FIXME: ExtractImage related APIs return empty dicts in
            # response
            if len(response) > 0:
                paramProperty = self.construct_response(response)
                csCmd.response_params.append(paramProperty)
        return csCmd

    def load_commands(self, apiStream):
        if apiStream is None:
            raise Exception("No APIs found through discovery")

        jsonOut = apiStream.readlines()
        assert len(jsonOut) > 0
        apiDict = json.loads(jsonOut[0])
        if 'listapisresponse' not in apiDict:
            raise Exception("API discovery plugin response failed")
        if 'count' not in apiDict['listapisresponse']:
            raise Exception("Malformed api response")

        apilist = apiDict['listapisresponse']['api']
        cmds = []
        for cmd in apilist:
            csCmd = self.load_command(cmd)
            cmds.append(csCmd)
        return cmds

    def generate_from_api(self, url):
        apiStream = urllib2.urlopen(url)
        cmds = self.load_commands(apiStream)
        self.generate(cmds)


def get_text(elements):
    return elements[0].childNodes[0].nodeValue.strip()


def exit_with_error(help_info, message):
    print message
    print help_info.print_help()
    exit(1)


def main():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output",
                      help="The path to the generated code entities")
    parser.add_option("-s", "--specfile", dest="spec",
                      help="The path and name of the api spec xml file, "
                           "i.e. ~/cloudstack/tools/apidoc/target/commands.xml")
    parser.add_option("-a", "--apiserver", dest="server",
                      help="The cloudstack management server (with open 8096) where apis are discovered, "
                           "i.e. localhost")
    (options, args) = parser.parse_args()

    if options.output is None:
        exit_with_error(parser, "Specify --output")
    if options.spec is None and options.server is None:
        exit_with_error(parser, "Specify either --specfile or --apierver")
    if options.spec is not None and options.server is not None:
        exit_with_error(parser, "Specify either --specfile or --apiserver, not both")

    use_specfile = options.spec is not None

    if use_specfile:
        if not os.path.exists(options.spec):
            exit_with_error(parser, "the spec file %s does not exist" % options.spec)

    folder = options.output
    if not os.path.exists(folder):
        os.mkdir(folder)
    apiModule = folder + "/csapi"
    if not os.path.exists(apiModule):
        os.mkdir(apiModule)
    modelModule = apiModule + "/model"
    if not os.path.exists(modelModule):
        os.mkdir(modelModule)

    if use_specfile:
        cg = XmlCodeGenerator(folder)
        cg.generate_from_file(options.spec)
    else:
        endpointUrl = 'http://%s:8096/client/api?command=listApis&response=json' % options.server
        cg = JsonCodeGenerator(folder)
        cg.generate_from_api(endpointUrl)


if __name__ == "__main__":
    main()
