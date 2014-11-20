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

"""Test data generation."""

import random
import os
import logging
import time
import string

from csapi.model import USER_ACC, ADMIN_ACC, DOMAIN_ACC
from csapi.model import BASIC, ADVANCED
from csapi.model import Domain, Zone, AccountType, Account, User
from csapi.account import AccountAPI


logger = logging.getLogger("cstest.random_data")
logger.setLevel(logging.DEBUG)

_chars = string.ascii_letters
_password_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-='
_tlds = ['com', 'org', 'net', 'nl', 'de']
_account_types = [USER_ACC, ADMIN_ACC, DOMAIN_ACC]
_network_types = [BASIC, ADVANCED]
_vowels = ['a', 'e', 'i', 'o', 'u']
_consonants = list([c for c in string.ascii_lowercase if not c in _vowels])
_wordchars = _vowels + _vowels + _vowels + _consonants
_booleans = [True, False]

class RandomValue(random.Random):
    log = logger

    def __init__(self):
        self.log = logger
        seed = os.environ.get('RANDOM_SEED', None)
        if seed is not None:
            seed = int(seed)
            self.log.debug('Using predefined random seed %s' % seed)
        else:
            seed = long(time.time() * 256)  # borrowed from random.py
            self.log.debug('Using generated random seed %s' % seed)
        super(RandomValue, self).__init__(seed)
    
    def random_bool(self):
        return self.choice(_booleans)

    def random_char(self, chars=None):
        if chars is None:
            chars = _wordchars
        return self.choice(chars)

    def random_word(self, length=None, chars=None):
        if length is None or length < 0:
            length = self.randint(3, 8)
        result = ''
        for i in xrange(length):
            result += self.random_char(chars=chars)
        return result

    def random_name(self, words=1):
        result = ''
        for i in xrange(words):
            result += self.random_char(chars=string.ascii_uppercase)
            result += self.random_word(chars=_wordchars)
            result += ' '
        result = result.strip()
        return result

    def random_string_id(self):
        result = ''
        length = 5 + self.randint(0, 5)
        result += self.random_word(length=length, chars=_wordchars)
        return result

    def random_username(self):
        return 'cstest-' + self.random_word(length=self.randint(5, 10), chars=string.ascii_lowercase)

    def random_account_name(self):
        return self.random_username()

    def random_tld(self):
        return self.choice(_tlds)

    def random_domain_name(self):
        return self.random_word(chars=string.ascii_lowercase) + '.' + self.random_tld()

    def random_email(self, username=None):
        if username is None:
            username = self.random_username()
        return username + '@' + self.random_domain_name()

    def random_password(self):
        return self.random_word(length=self.randint(5, 10))

    def random_account_type(self):
        return self.choice(_account_types)
    
    def random_network_type(self):
        return self.choice(_network_types)


class RandomData(RandomValue):
    def __init__(self, account_api=None):
        """
        :type account_api: AccountAPI
        """
        super(RandomData, self).__init__()
        self.account_api = account_api
        if self.account_api is None:
            self.account_api = AccountAPI()

    def random_domain(self):
        """
        :rtype: Domain
        """
        if self.random_bool():
            networkdomain = self.random_domain_name()
        else:
            networkdomain = None
        return Domain(
            name=self.random_string_id(),
            networkdomain=networkdomain
        )

    def random_zone(self):
        """
        :rtype: Zone
        """
        return Zone(
            dns1='8.8.8.8',
            internaldns1='10.1.1.1',
            name=self.random_string_id(),
            networktype=self.random_network_type(),
            guestcidraddress='10.1.1.0/24',
        )

    def random_account(self, account_type=None):
        """
        :type account_type: AccountType|int 
        :rtype: Account
        """
        if account_type is None:
            account_type = self.random_account_type()

        username = self.random_username()
        return Account(
            username=username,
            name=username,
            password=self.random_password(),
            firstname=self.random_name(),
            lastname=self.random_name(),
            email=self.random_email(username=username),
            accounttype=account_type
        )

    def random_user(self, account=None):
        """
        :type account: Account 
        :rtype: User
        """
        username = self.random_username()
        if account is None:
            account = self.choose_account()

        return User(
            account=account.name,
            domainid=account.domainid,
            username=username,
            password=self.random_password(),
            firstname=self.random_name(),
            lastname=self.random_name(),
            email=self.random_email(username=username),
        )

    def choose_account(self):
        """
        :rtype: Account
        """
        accounts = self.account_api.list(listall=False)
        return self.choice(accounts)

    def choose_user(self):
        """
        :rtype: User
        """
        accounts = self.user_api.list(listall=False, account=self.choose_account().name)
        return self.choice(accounts)
