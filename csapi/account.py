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

from marvin.cloudstackAPI.createAccount import createAccountCmd
from marvin.cloudstackAPI.updateAccount import updateAccountCmd
from marvin.cloudstackAPI.listAccounts import listAccountsCmd
from marvin.cloudstackAPI.deleteAccount import deleteAccountCmd

from apiclient import CloudStackObjectAPI, copy_to_object, new_object
from apiclient import CloudstackNoResultsException, CloudstackAPIFailureException, CloudstackMultipleResultsException
from csapi.model import Account


class AccountAPI(CloudStackObjectAPI):
    def create(self, account):
        """:type account: Account"""
        cmd = new_object(createAccountCmd, account)
        created = self.api_client().createAccount(cmd, method="POST")
        return new_object(Account, created, set_all=True)

    def update(self, account):
        """:type account: Account"""
        cmd = new_object(updateAccountCmd, account)
        updated = self.api_client().updateAccount(cmd, method="POST")
        return new_object(Account, updated, set_all=True)

    def delete(self, account):
        """:type account: Account|int"""
        if isinstance(account, int):
            account_id = account
        else:
            account_id = account.id
        cmd = deleteAccountCmd()
        cmd.id = account_id
        result = self.api_client().deleteAccount(cmd, method="POST")
        if not result.success:
            raise CloudstackAPIFailureException(
                "deletion failed for id %s" % account_id)

    def delete_all(self, *args):
        """:type *args: list[Account]"""
        cmd = listAccountsCmd()
        cmd.listall = True
        results = self.api_client().listAccounts(cmd)
        for account in args:
            for result in results:
                if account.name == result.name:
                    self.delete(result)

    def list(self, **kwargs):
        """:rtype: collections.Sequence[Account]"""
        cmd = listAccountsCmd()
        copy_to_object(cmd, kwargs)
        results = self.api_client().listAccounts(cmd)
        if results is None:
            return []
        return list([new_object(Account, a, set_all=True) for a in results])

    def find(self, **kwargs):
        """:rtype: Account"""
        if not 'listall' in kwargs:
            kwargs = dict(kwargs)
            kwargs['listall'] = True
        results = self.list(**kwargs)
        matches = len(results)
        if matches == 0:
            raise CloudstackNoResultsException(
                "No results found matching %s" % repr(kwargs))
        elif matches == 1:
            return results[0]
        else:
            raise CloudstackMultipleResultsException(
                "%s results found matching %s" % (matches, repr(kwargs)))
