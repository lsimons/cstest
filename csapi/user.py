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

from marvin.cloudstackAPI.createUser import createUserCmd
from marvin.cloudstackAPI.updateUser import updateUserCmd
from marvin.cloudstackAPI.listUsers import listUsersCmd
from marvin.cloudstackAPI.deleteUser import deleteUserCmd

from apiclient import CloudStackObjectAPI, copy_to_object, new_object
from apiclient import CloudstackNoResultsException, CloudstackAPIFailureException, CloudstackMultipleResultsException
from csapi.model import User


class UserAPI(CloudStackObjectAPI):
    def create(self, user):
        """:type user: User"""
        cmd = new_object(createUserCmd, user)
        created = self.api_client().createUser(cmd, method="POST")
        return new_object(User, created, set_all=True)

    def update(self, user):
        """:type user: User"""
        cmd = new_object(updateUserCmd, user)
        updated = self.api_client().updateUser(cmd, method="POST")
        return new_object(User, updated, set_all=True)

    def delete(self, user):
        """:type user: User|int"""
        if isinstance(user, int):
            user_id = user
        else:
            user_id = user.id
        cmd = deleteUserCmd()
        cmd.id = user_id
        result = self.api_client().deleteUser(cmd, method="POST")
        if not result.success:
            raise CloudstackAPIFailureException(
                "deletion failed for id %s" % user_id)

    def delete_all(self, *args):
        """:type *args: list[User]"""
        cmd = listUsersCmd()
        cmd.listall = True
        results = self.api_client().listUsers(cmd)
        for user in args:
            for result in results:
                if user.username == result.username:
                    self.delete(result)

    def list(self, **kwargs):
        """:rtype: collections.Sequence[User]"""
        cmd = listUsersCmd()
        copy_to_object(cmd, kwargs)
        results = self.api_client().listUsers(cmd)
        if results is None:
            return []
        return list([new_object(User, a, set_all=True) for a in results])

    def find(self, **kwargs):
        """:rtype: User"""
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
