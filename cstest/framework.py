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

"""Basic integration tests for CIT environment."""

import unittest
import logging

from csapi.apiclient import CSConnection, CloudStackAPIClient, CloudstackAPIException
from csapi.domain import DomainAPI
from csapi.zone import ZoneAPI
from csapi.account import AccountAPI
from csapi.user import UserAPI
from cstest.random_data import RandomData
from csapi.model import ADMIN_ACC, DOMAIN_ACC, USER_ACC, BASIC, ADVANCED

logger = logging.getLogger("cstest")
logger.setLevel(logging.DEBUG)


def failing(fn):
    """Decorate tests to indicate they are currently failing due to ."""
    def decorated(self, *args, **kwargs):
        try:
            fn(self, *args, **kwargs)
            logger.warn("Expected failure of %s but it passed" % fn)
        except (AssertionError, CloudstackAPIException) as e:
            logger.info("Expected failure of %s, got %s" % (fn, str(e)))
    return decorated


class CITTestCase(unittest.TestCase):
    """Simplified marvin-compatible test case that does not do any complex init stuff."""
    connection = None
    api_client = None
    domain_api = None
    zone_api = None
    account_api = None
    user_api = None
    log = logger
    config = {}
    data = None
    __zone = None
    __domain = None
    __admin_account = None
    __admin_user = None
    __domain_account = None
    __domain_user = None

    @classmethod
    def setUpClass(cls):
        cls.connection = CSConnection()
        cls.api_client = CloudStackAPIClient(cls.connection)
        cls.domain_api = DomainAPI()
        cls.zone_api = ZoneAPI()
        cls.account_api = AccountAPI()
        cls.user_api = UserAPI()
        cls.log = logger
        cls.data = RandomData()

    @property
    def domain(self):
        if self.__domain is not None:
            return self.__domain
        domains = self.domain_api.list()
        if len(domains) == 0:
            self.__domain = self.domain_api.create(self.data.random_domain())
        else:
            self.__domain = self.data.choice(domains)
        return self.__domain

    @property
    def zone(self):
        if self.__zone is not None:
            return self.__zone
        zones = self.zone_api.list()
        if len(zones) == 0:
            zone = self.data.random_zone()
            zone.domainid = self.domain.id
            zone.securitygroupenabled = False
            zone.localstorageenabled = True
            zone.networktype = ADVANCED
            self.__zone = self.zone_api.create(zone)
        else:
            self.__zone = self.data.choice(zones)
        return self.__zone

    @property
    def admin_account(self):
        return self.__get_account('_admin_account', account_type=ADMIN_ACC)
    
    @property
    def admin_user(self):
        return self.__get_user_for_account('_admin_user', self.admin_account)

    @property
    def domain_account(self):
        return self.__get_account('_domain_account', account_type=DOMAIN_ACC)

    @property
    def domain_user(self):
        return self.__get_user_for_account('_domain_user', self.domain_account)

    @property
    def user_account(self):
        return self.__get_account('_user_account', account_type=USER_ACC)

    @property
    def user(self):
        return self.__get_user_for_account('_user', self.user_account)

    def __get_account(self, property_name, account_type=ADMIN_ACC, domain=None):
        account = getattr(self, property_name, None)
        if account is None:
            if account_type == DOMAIN_ACC and domain is None:
                domain = self.domain
            accounts = self.account_api.list(accounttype=account_type)
            accounts = list([a for a in accounts if domain is None or a.domainid == domain.id])
            if len(accounts) == 0:
                account = self.data.random_account(account_type=DOMAIN_ACC)
                if domain is not None:
                    account.domainid = domain.id
                account = self.account_api.create(self.data.random_account(account_type=account_type))
            setattr(self, property_name, account)
        return account        

    def __get_user_for_account(self, property_name, account):
        user = getattr(self, property_name, None) 
        if user is None:
            users = self.user_api.list(account=account.name)
            if len(users) == 0:
                user = self.data.random_user(account)
                user = self.user_api.create(user)
            else:
                user = self.data.choice(users)
            setattr(self, property_name, user)
        return user
