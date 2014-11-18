# Licensed to the Apache Software Foundation (ASF) under one
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
Basic tests of account and user management.
"""

from csapi.model import USER_ACC, DOMAIN_ACC, ADMIN_ACC
from cstest.framework import CITTestCase, failing
from csapi.apiclient import CloudstackAPIException

class AccountTestCase(CITTestCase):
    @classmethod
    def setUpClass(cls):
        super(AccountTestCase, cls).setUpClass()

    def test_account_management(self):
        for i in xrange(3):
            for account_type in [USER_ACC, DOMAIN_ACC, ADMIN_ACC]:
                account = self.data.random_account(account_type=account_type)
                created_account = self.account_api.create(account)
                self.__confirm_account(created_account)
                if i % 2 == 0:  # keeping some accounts for other tests to use
                    self.account_api.delete(created_account)

    def test_duplicate_account_error(self):
        account = self.data.random_account()
        self.account_api.create(account)
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.account_api.create(account)

    @failing
    def test_delete_and_recreate_same_account(self):
        account = self.data.random_account()
        created_account = self.account_api.create(account)
        self.account_api.delete(created_account)
        self.account_api.create(account)

    def test_same_account_name_in_different_domains(self):
        domain1 = self.domain
        account1 = self.data.random_account(account_type=DOMAIN_ACC)
        account1.domainid = domain1.id
        self.account_api.create(account1)
        domain2 = self.domain_api.create(self.data.random_domain())
        account2 = self.data.random_account(account_type=DOMAIN_ACC)
        account2.name = account1.name
        account2.domainid = domain2.id
        self.account_api.create(account2)

    def __confirm_account(self, account):
        """Confirms provided account exists by looking it up."""
        self.account_api.find(name=account.name)

    def __confirm_user(self, user):
        """Confirms provided user exists by looking it up."""
        self.user_api.find(username=user.username)


if __name__ == '__main__':
    from unittest import main
    main()
