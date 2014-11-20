[include "license.tpl"]

from apiclient import CloudStackObjectAPI, copy_to_object, new_object
from apiclient import CloudstackNoResultsException, CloudstackAPIFailureException, CloudstackMultipleResultsException
from csapi.model.[package_name] import [model_name]


class [model_name]API(CloudStackObjectAPI):
    def create(self, [variable_name]):
        """:type [variable_name]: [model_name]"""
        raise Exception('todo')
    
    def update(self, [variable_name]):
        """:type [variable_name]: [model_name]"""
        raise Exception('todo')
    
    def delete(self, [variable_name]):
        """:type [variable_name]: [model_name]"""
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

from .base import Struct


class [model_name](Struct):
def __init__(self, **kwargs):[for fields]
"""
[fields.desc] [is fields.pythonType ""][else]
:type: [fields.pythonType][end]
"""
self.[fields.name] = None[end]

super([model_name], self).__init__(**kwargs)
