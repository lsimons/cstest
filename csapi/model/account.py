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

class AccountType(int):
    def __new__(cls, value):
        if value < 0 or value > 2:
            raise ValueError("AccountType should be 0, 1, or 2")
        return super(AccountType, cls).__new__(cls, value)


USER_ACC = AccountType(0)
ADMIN_ACC = AccountType(1)
DOMAIN_ACC = AccountType(2)


class Account(Struct):
    def __init__(self, **kwargs):
        """:type: int"""
        self.id = None
        """:type: string"""
        self.name = None
        """:type: int"""
        self.accounttype = None
        """:type: string"""
        self.email = None
        """:type: string"""
        self.firstname = None
        """:type: string"""
        self.lastname = None
        """:type: string"""
        self.password = None
        """:type: string"""
        self.username = None
        """:type: string"""
        self.account = None
        """:type: dict"""
        self.accountdetails = []
        """:type: string"""
        self.accountid = None
        """:type: string"""
        self.domainid = None
        """:type: string"""
        self.networkdomain = None
        """:type: string"""
        self.timezone = None
        """:type: string"""
        self.userid = None

        super(Account, self).__init__(**kwargs)
