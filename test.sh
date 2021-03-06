#!/bin/bash
#
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

# convenience wrapper for invoking unittest.
# Can also use any other python test runner.

BASEDIR="."
function find_basedir() {
  # from http://stackoverflow.com/a/246128
  local SOURCE="${BASH_SOURCE[0]}"
  local DIR=""

  while [ -h "$SOURCE" ]; do
    # resolve $SOURCE until the file is no longer a symlink
    DIR="$( cd -P "$( dirname "${SOURCE}" )" && pwd )"
    SOURCE="$(readlink "${SOURCE}")"
    # if $SOURCE was a relative symlink, we need to resolve it relative
    # to the path where the symlink file was located
    [[ ${SOURCE} != /* ]] && SOURCE="${DIR}/${SOURCE}"
  done
  DIR="$( cd -P "$( dirname "${SOURCE}" )" && pwd )"

  BASEDIR="${DIR}"
}
find_basedir

PYTHONPATH="${BASEDIR}:${PYTHONPATH}"

python -m unittest discover "$@"
