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
Basic tests of zone management.
"""

from cstest.framework import CITTestCase
from csapi.apiclient import CloudstackAPIException
from csapi.model import Zone


class ZoneTestCase(CITTestCase):
    @classmethod
    def setUpClass(cls):
        super(ZoneTestCase, cls).setUpClass()

    def test_zone_management(self):
        for i in xrange(3):
            zone = self.data.random_zone()
            created_zone = self.zone_api.create(zone)
            self.__confirm_zone(created_zone)

            if 1 % 2 == 0:  # keeping some zones for other tests to use
                self.zone_api.delete(created_zone)

    def test_duplicate_zone_error(self):
        zone = self.data.random_zone()
        self.zone_api.create(zone)
        with self.assertRaisesRegexp(CloudstackAPIException, 'exists'):
            self.zone_api.create(zone)

    def test_update_zone_without_changes(self):
        zone = self.data.random_zone()
        zone = self.zone_api.create(zone)
        self.zone_api.update(zone)

    def test_delete_zone(self):
        zone = self.zone_api.create(self.data.random_zone())
        self.zone_api.delete(zone)
        with self.assertRaisesRegexp(CloudstackAPIException, 'found'):
            self.zone_api.find(name=zone.name)

    def __confirm_zone(self, zone):
        """Confirms provided zone exists by looking it up."""
        self.zone_api.find(name=zone.name)
        if zone.id is not None:
            self.__verify_zone(zone)

    def __verify_zone(self, zone):
        assert isinstance(zone, Zone)
        assert zone.id is not None
        assert zone.name is not None
        assert zone.name is not ""


if __name__ == '__main__':
    from unittest import main
    main()
