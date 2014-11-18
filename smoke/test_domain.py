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
Basic tests of domain management.
"""

from cstest.framework import CITTestCase, failing
from csapi.apiclient import CloudstackAPIException
from csapi.model import Domain, DOMAIN_ACC


class DomainTestCase(CITTestCase):
    @classmethod
    def setUpClass(cls):
        super(DomainTestCase, cls).setUpClass()

    def test_domain_management(self):
        for i in xrange(3):
            domain = self.data.random_domain()
            created_domain = self.domain_api.create(domain)
            self.__confirm_domain(created_domain)

            if 1 % 2 == 0:  # keeping some domains for other tests to use
                self.domain_api.delete(created_domain)
    
    def test_domain_hierarchy(self):
        domain = self.data.random_domain()
        created_domain = self.domain_api.create(domain)
        self.__verify_domain(created_domain)
        child_domain = self.data.random_domain()
        child_domain.parentdomainid = created_domain.id
        created_child_domain = self.domain_api.create(child_domain)
        self.__verify_domain(created_child_domain)
        found_domain = self.domain_api.find(name=created_domain.name)
        assert found_domain.haschild == True, \
            "adding child to domain should set its haschild to True"

    @failing
    def test_cannot_move_domain_after_creation_error(self):
        # parentdomainid is silently ignored on update!
        domain = self.data.random_domain()
        created_domain = self.domain_api.create(domain)
        child_domain = self.data.random_domain()
        child_domain.parentdomainid = created_domain.id
        created_child_domain = self.domain_api.create(child_domain)
        other_domain = self.data.random_domain()
        created_other_domain = self.domain_api.create(other_domain)
        created_child_domain.parentdomainid = created_other_domain.id
        with self.assertRaisesRegexp(CloudstackAPIException, 'cannot.*?move'):
            self.domain_api.update(created_child_domain)

    def test_duplicate_domain_error(self):
        domain = self.data.random_domain()
        self.domain_api.create(domain)
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.domain_api.create(domain)
    
    def test_domain_with_same_name_elsewhere_in_hierarchy_error(self):
        domain = self.data.random_domain()
        created_domain = self.domain_api.create(domain)
        child_domain = self.data.random_domain()
        child_domain.parentdomainid = created_domain.id
        created_child_domain = self.domain_api.create(child_domain)
        grandchild_domain = self.data.random_domain()
        grandchild_domain.name = domain.name
        grandchild_domain.id = created_child_domain.id
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.domain_api.create(grandchild_domain)
    
    def test_rename_domain(self):
        domain = self.data.random_domain()
        orig_name = domain.name
        domain = self.domain_api.create(domain)
        domain.name = self.data.random_string_id()
        self.domain_api.update(domain)
        self.__confirm_no_domain(orig_name)

    def test_update_domain_without_changes(self):
        domain = self.data.random_domain()
        domain = self.domain_api.create(domain)
        self.domain_api.update(domain)

    def test_update_domain_with_conflicting_name(self):
        domain = self.domain_api.create(self.data.random_domain())
        other_domain = self.domain_api.create(self.data.random_domain())
        other_domain.name = domain.name
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.domain_api.update(other_domain)

    def test_update_domain_with_network_domain(self):
        domain = self.domain_api.create(self.data.random_domain())
        domain.networkdomain = 'foo.bar'
        self.domain_api.update(domain)

    def test_delete_domain(self):
        domain = self.domain_api.create(self.data.random_domain())
        self.domain_api.delete(domain)
        self.__confirm_no_domain(domain)

    def test_delete_domain_with_active_accounts_error(self):
        domain = self.domain_api.create(self.data.random_domain())
        account = self.data.random_account(account_type=DOMAIN_ACC)
        account.domainid = domain.id
        self.account_api.create(account)
        with self.assertRaisesRegexp(Exception, 'users'):
            # todo exception message should contain 'account' if account exists
            # todo exception type should not be Exception
            self.domain_api.delete(domain)
        self.__verify_domain(domain)
    
    def test_domain_with_too_long_name_error(self):
        domain = self.data.random_domain()
        domain.name = domain.name + "padding" * 1024
        with self.assertRaisesRegexp(CloudstackAPIException, 'length'):
            self.domain_api.create(domain)
        # can't do this since the name is too long ...
        # self.__confirm_no_domain(orig_name)
        with self.assertRaisesRegexp(CloudstackAPIException, 'length'):
            self.domain_api.find(name=domain.name)

    def test_rename_domain_with_too_long_name_error(self):
        domain = self.data.random_domain()
        orig_name = domain.name
        domain = self.domain_api.create(domain)
        domain.name = domain.name + "padding" * 1024
        with self.assertRaisesRegexp(CloudstackAPIException, 'length'):
            self.domain_api.create(domain)
        # can't do this since the name is too long ...
        # self.__confirm_no_domain(orig_name)
        with self.assertRaisesRegexp(CloudstackAPIException, 'length'):
            self.domain_api.find(name=domain.name)

    def test_domain_with_too_long_network_domain_error(self):
        domain = self.data.random_domain()
        domain.networkdomain = "network" + "padding" * 1024
        with self.assertRaisesRegexp(CloudstackAPIException, 'length'):
            self.domain_api.create(domain)
            
        self.__confirm_no_domain(domain)
        
    def test_create_domain_with_invalid_network_domain_error(self):
        domain = self.data.random_domain()
        domain.networkdomain = 'domains can\'t have spaces'
        with self.assertRaisesRegexp(CloudstackAPIException, '(I|i)nvalid'):
            self.domain_api.create(domain)
        self.__confirm_no_domain(domain)

    def test_update_domain_with_invalid_network_domain_error(self):
        domain = self.domain_api.create(self.data.random_domain())
        domain.networkdomain = 'domains can\'t have spaces'
        with self.assertRaisesRegexp(CloudstackAPIException, '(I|i)nvalid'):
            self.domain_api.update(domain)

    def __confirm_no_domain(self, domain):
        if not isinstance(domain, basestring):
            domain = domain.name
        with self.assertRaisesRegexp(CloudstackAPIException, 'found'):
            self.domain_api.find(name=domain)

    def __confirm_domain(self, domain):
        """Confirms provided domain exists by looking it up."""
        if not isinstance(domain, basestring):
            domain = domain.name
        domain = self.domain_api.find(name=domain)
        if domain.id is not None:
            self.__verify_domain(domain)

    def __verify_domain(self, domain):
        assert isinstance(domain, Domain)
        assert domain.id is not None
        assert domain.name is not None
        assert domain.name is not ""
        assert domain.haschild in [True, False, None]
        assert domain.networkdomain is not ""
        assert domain.path is not None
        assert isinstance(domain.path, basestring)
        assert domain.path.startswith("ROOT")


if __name__ == '__main__':
    from unittest import main
    main()
