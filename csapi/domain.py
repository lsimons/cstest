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

from marvin.cloudstackAPI.createDomain import createDomainCmd
from marvin.cloudstackAPI.updateDomain import updateDomainCmd
from marvin.cloudstackAPI.listDomains import listDomainsCmd
from marvin.cloudstackAPI.deleteDomain import deleteDomainCmd

from apiclient import CloudStackObjectAPI, copy_to_object, new_object
from apiclient import CloudstackNoResultsException, CloudstackAPIFailureException, CloudstackMultipleResultsException
from csapi.model import Domain


class DomainAPI(CloudStackObjectAPI):
    def create(self, domain):
        """:type domain: Domain"""
        cmd = new_object(createDomainCmd, domain)
        created = self.api_client().createDomain(cmd, method="POST")
        return new_object(Domain, created, set_all=True)

    def update(self, domain):
        """:type domain: Domain"""
        cmd = new_object(updateDomainCmd, domain)
        updated = self.api_client().updateDomain(cmd, method="POST")
        return new_object(Domain, updated, set_all=True)

    def delete(self, domain):
        """:type domain: Domain|int"""
        if isinstance(domain, int):
            domain_id = domain
        else:
            domain_id = domain.id
        cmd = deleteDomainCmd()
        cmd.id = domain_id
        result = self.api_client().deleteDomain(cmd, method="POST")
        if not result.success:
            raise CloudstackAPIFailureException(
                "deletion failed for id %s" % domain_id)

    def delete_all(self, *args):
        """:type *args: list[Domain]"""
        cmd = listDomainsCmd()
        cmd.listall = True
        results = self.api_client().listDomains(cmd)
        for domain in args:
            for result in results:
                if domain.name == result.name:
                    self.delete(result)

    def list(self, **kwargs):
        """:rtype: collections.Sequence[Domain]"""
        cmd = listDomainsCmd()
        copy_to_object(cmd, kwargs)
        results = self.api_client().listDomains(cmd)
        if results is None:
            return []
        return list([new_object(Domain, a, set_all=True) for a in results])

    def find(self, **kwargs):
        """:rtype: Domain"""
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
