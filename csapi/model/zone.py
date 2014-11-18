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


class NetworkType(str):
    def __new__(cls, value):
        return super(NetworkType, cls).__new__(cls, value)


BASIC = NetworkType("Basic")
ADVANCED = NetworkType("Advanced")


class Zone(Struct):
    def __init__(self, **kwargs):
        """:type: int"""
        self.id = None
        """:type: string"""
        self.dns1 = None
        """:type: string"""
        self.internaldns1 = None
        """:type: string"""
        self.name = None
        """:type: string"""
        self.networktype = None
        """:type: string"""
        self.allocationstate = None
        """:type: string"""
        self.dns2 = None
        """:type: string"""
        self.domain = None
        """:type: string"""
        self.domainid = None
        """:type: string"""
        self.guestcidraddress = None
        """:type: string"""
        self.internaldns2 = None
        """:type: string"""
        self.ip6dns1 = None
        """:type: string"""
        self.ip6dns2 = None
        """:type: bool"""
        self.localstorageenabled = None
        """:type: bool"""
        self.securitygroupenabled = None

        super(Zone, self).__init__(**kwargs)
