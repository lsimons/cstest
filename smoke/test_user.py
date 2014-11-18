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
Basic tests of user management.
"""

from csapi.model import DOMAIN_ACC, ADMIN_ACC
from cstest.framework import CITTestCase, failing
from csapi.apiclient import CloudstackAPIException

class UserTestCase(CITTestCase):
    @classmethod
    def setUpClass(cls):
        super(UserTestCase, cls).setUpClass()

    def test_user_management(self):
        for i in xrange(3):
            for account in [self.admin_account, self.domain_account, self.user_account]:
                user = self.data.random_user(account=account)
                created_user = self.user_api.create(user)
                self.__confirm_user(created_user)
                if i % 2 == 0:  # keeping some users for other tests to use
                    self.user_api.delete(created_user)

    def test_duplicate_user_error(self):
        user = self.data.random_user()
        self.user_api.create(user)
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.user_api.create(user)

    def test_same_username_in_different_accounts_same_domain_error(self):
        account1 = self.account_api.create(self.data.random_account(account_type=ADMIN_ACC))
        account2 = self.account_api.create(self.data.random_account(account_type=ADMIN_ACC))
        user1 = self.data.random_user(account=account1)
        user2 = self.data.random_user(account=account2)
        user2.username = user1.username
        self.user_api.create(user1)
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.user_api.create(user2)
    
    def test_same_username_in_different_domains(self):
        domain1 = self.domain
        account1 = self.data.random_account(account_type=DOMAIN_ACC)
        account1.domainid = domain1.id
        self.account_api.create(account1)
        domain2 = self.domain_api.create(self.data.random_domain())
        account2 = self.data.random_account(account_type=DOMAIN_ACC)
        account2.domainid = domain2.id
        self.account_api.create(account2)

        user1 = self.data.random_user(account=account1)
        user2 = self.data.random_user(account=account2)
        user2.username = user1.username
        self.user_api.create(user1)
        self.user_api.create(user2)

    @failing
    def test_delete_and_recreate_same_user(self):
        account = self.data.random_account()
        self.account_api.create(account)
        user = self.data.random_user(account=account)
        created_user = self.user_api.create(user)
        self.user_api.delete(created_user)
        self.user_api.create(user)

    @failing
    def test_user_domain_should_derive_from_account_domain(self):
        domain = self.domain
        account = self.data.random_account(account_type=DOMAIN_ACC)
        account.domainid = domain.id
        self.account_api.create(account)

        user = self.data.random_user(account=account)
        user.domainid = None
        assert domain.id == user.domainid, "User in account gets same domain as that account by default"

    def __confirm_user(self, user):
        """Confirms provided user exists by looking it up."""
        self.user_api.find(username=user.username)


if __name__ == '__main__':
    from unittest import main
    main()
