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

from collections import MutableMapping


class Struct(MutableMapping):
    """Dictionary-like object that also supports property syntax."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def __delitem__(self, key):
        return self.__dict__.__delitem__(key)

    def __len__(self):
        return self.__dict__.__len__()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join(
            ["%s=%s" % (k, repr(v)) for k, v in self.__dict__.iteritems()
             if not callable(v)]))
