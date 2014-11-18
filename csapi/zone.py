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

from marvin.cloudstackAPI.createZone import createZoneCmd
from marvin.cloudstackAPI.updateZone import updateZoneCmd
from marvin.cloudstackAPI.listZones import listZonesCmd
from marvin.cloudstackAPI.deleteZone import deleteZoneCmd

from apiclient import CloudStackObjectAPI, copy_to_object, new_object
from apiclient import CloudstackNoResultsException, CloudstackAPIFailureException, CloudstackMultipleResultsException
from csapi.model import Zone


class ZoneAPI(CloudStackObjectAPI):
    def create(self, zone):
        """:type zone: Zone"""
        cmd = new_object(createZoneCmd, zone)
        created = self.api_client().createZone(cmd, method="POST")
        return new_object(Zone, created, set_all=True)

    def update(self, zone):
        """:type zone: Zone"""
        cmd = new_object(updateZoneCmd, zone)
        updated = self.api_client().updateZone(cmd, method="POST")
        return new_object(Zone, updated, set_all=True)

    def delete(self, zone):
        """:type zone: Zone|int"""
        if isinstance(zone, int):
            zone_id = zone
        else:
            zone_id = zone.id
        cmd = deleteZoneCmd()
        cmd.id = zone_id
        result = self.api_client().deleteZone(cmd, method="POST")
        if not result.success:
            raise CloudstackAPIFailureException(
                "deletion failed for id %s" % zone_id)

    def delete_all(self, *args):
        """:type *args: list[Zone]"""
        cmd = listZonesCmd()
        cmd.listall = True
        results = self.api_client().listZones(cmd)
        for zone in args:
            for result in results:
                if zone.name == result.name:
                    self.delete(result)

    def list(self, **kwargs):
        """:rtype: collections.Sequence[Zone]"""
        cmd = listZonesCmd()
        copy_to_object(cmd, kwargs)
        results = self.api_client().listZones(cmd)
        if results is None:
            return []
        return list([new_object(Zone, a, set_all=True) for a in results])

    def find(self, **kwargs):
        """:rtype: Zone"""
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
