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

from .base import Struct


class PhysicalNetwork(Struct):
    def __init__(self, **kwargs):
        """:type: int"""
        self.id = None
        """the PhysicalNetwork ID for the physical network"""
        self.PhysicalNetworkid = None


        super(PhysicalNetwork, self).__init__(**kwargs)

class createPhysicalNetworkCmd (baseCmd):
    typeInfo = {}
    def __init__(self):
        self.isAsync = "true"
        """the name of the physical network"""
        """Required"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the PhysicalNetwork ID for the physical network"""
        """Required"""
        self.PhysicalNetworkid = None
        self.typeInfo['PhysicalNetworkid'] = 'uuid'
        """the broadcast domain range for the physical network[Pod or PhysicalNetwork]. In Acton release it can be PhysicalNetwork only in Advance PhysicalNetwork, and Pod in Basic"""
        self.broadcastdomainrange = None
        self.typeInfo['broadcastdomainrange'] = 'string'
        """domain ID of the account owning a physical network"""
        self.domainid = None
        self.typeInfo['domainid'] = 'uuid'
        """the isolation method for the physical network[VLAN/L3/GRE]"""
        self.isolationmethods = []
        self.typeInfo['isolationmethods'] = 'list'
        """the speed for the physical network[1G/10G]"""
        self.networkspeed = None
        self.typeInfo['networkspeed'] = 'string'
        """Tag the physical network"""
        self.tags = []
        self.typeInfo['tags'] = 'list'
        """the VLAN for the physical network"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        self.required = ["name","PhysicalNetworkid",]

class createPhysicalNetworkResponse (baseResponse):
    typeInfo = {}
    def __init__(self):
        """the uuid of the physical network"""
        self.id = None
        self.typeInfo['id'] = 'string'
        """Broadcast domain range of the physical network"""
        self.broadcastdomainrange = None
        self.typeInfo['broadcastdomainrange'] = 'string'
        """the domain id of the physical network owner"""
        self.domainid = None
        self.typeInfo['domainid'] = 'string'
        """isolation methods"""
        self.isolationmethods = None
        self.typeInfo['isolationmethods'] = 'string'
        """name of the physical network"""
        self.name = None
        self.typeInfo['name'] = 'string'
        """the speed of the physical network"""
        self.networkspeed = None
        self.typeInfo['networkspeed'] = 'string'
        """state of the physical network"""
        self.state = None
        self.typeInfo['state'] = 'string'
        """comma separated tag"""
        self.tags = None
        self.typeInfo['tags'] = 'string'
        """the vlan of the physical network"""
        self.vlan = None
        self.typeInfo['vlan'] = 'string'
        """PhysicalNetwork id of the physical network"""
        self.PhysicalNetworkid = None
        self.typeInfo['PhysicalNetworkid'] = 'string'

