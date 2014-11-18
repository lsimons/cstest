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

import os
import sys
import logging
import re
import pprint
from xml.etree import ElementTree as ET
from collections import namedtuple, Mapping

import requests
from marvin.cloudstackConnection import CSConnection as MarvinCSConnection
from marvin.cloudstackException import CloudstackAPIException


from marvin.cloudstackAPI.cloudstackAPIClient import CloudStackAPIClient as MarvinCloudStackAPIClient
from csapi.model import Struct

TRACE = os.environ.get('TRACE', 0) == '1'
DEBUG = TRACE or os.environ.get('DEBUG', 0) == '1'

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("csapi")
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if TRACE:
    import httplib

    httplib.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def copy_to_object(obj, d, set_all=False):
    """Utility function to apply dict-like objects onto object properties.
    
    :type obj: object
    :type d: object | dict
    :type set_all: bool
    """
    mapping = d
    if not isinstance(d, Mapping):
        mapping = d.__dict__
    if set_all:
        for key, val in mapping.iteritems():
            if not callable(val):
                setattr(obj, key, val)
    else:
        for key, val in obj.__dict__.iteritems():
            if not callable(val) and key in mapping:
                setattr(obj, key, mapping.get(key))
    return obj


def new_object(constructor, d, set_all=False):
    """
    Utility function to apply dict-like objects onto new instance of a type.
    
    :type constructor: callable
    :type d: object
    :type set_all: bool
    """
    result = constructor()
    copy_to_object(result, d, set_all=set_all)
    return result


class CloudstackAPIFailureException(CloudstackAPIException):
    pass


class CloudstackNoResultsException(CloudstackAPIException):
    pass


class CloudstackMultipleResultsException(CloudstackAPIException):
    pass


class CSConnection(MarvinCSConnection):
    """Simplified CSConnection that provides sane defaults."""

    # noinspection PyUnresolvedReferences
    def __init__(self, **kw):
        global logger
        self.log = logger
        env = os.environ
        conf = dict(
            asyncTimeout=10,
            host=kw.get('host', env.get('CS_HOST', 'localhost')),
            port=kw.get('port', int(env.get('CS_PORT', '8080'))),
            user=kw.get('user', env.get('CS_USER', 'admin')),
            password=kw.get('password', env.get('CS_PASSWORD', 'password')),
            domain=kw.get('domain', env.get('CS_DOMAIN', None)),
            certCAPath='NA',
            certPath='NA',
            path='client/api',
            apiKey=kw.get('apiKey', env.get('CS_API_KEY', None)),
            secretKey=kw.get('secretKey', env.get('CS_SECRET_KEY', None)),
            protocol=kw.get('protocol', env.get('CS_PROTOCOL', None)),
            baseUrl=kw.get('baseUrl', env.get('CS_BASE_URL', None))
        )
        conf['mgtSvrIp'] = conf['host']  # why....
        conf['securityKey'] = conf['secretKey']  # oh god why???
        conf['passwd'] = conf['password']  # some consistency != foolish
        conf['useHttps'] = False
        conf = Struct(**conf)
        if conf.protocol is None:
            if conf.port == 443:
                conf.protocol = 'https'
                conf.useHttps = True
            else:
                conf.protocol = 'http'
                conf.useHttps = False
        if conf.baseUrl is None:
            conf.baseUrl = "%s://%s:%d/%s" % (
                conf.protocol, conf.host, conf.port, conf.path)
        merged = dict()
        merged.update(env)
        merged.update(kw)
        merged.update(conf)
        merged = Struct(**merged)

        self.log.info("Attempting a connection to %s" % merged.baseUrl)

        self.__find_api_keys(merged)

        super(CSConnection, self).__init__(
            merged, asyncTimeout=conf.asyncTimeout, logger=self.log, path=conf.path)

    def post(self, url, data=None, **kwargs):
        result = requests.post(url, data=dict(data), **kwargs)
        result.raise_for_status()
        if TRACE and hasattr(result, 'text') and self.log.isEnabledFor(logging.DEBUG):
            try:
                doc = ET.fromstring(result.text)
                print 'body:',
                ET.ElementTree(doc).write(sys.stdout)
            except SyntaxError:
                print 'body:', result.text
        return result

    @staticmethod
    def __get_session_id(r):
        cookies = r.headers['Set-cookie']
        match_obj = re.match(r'.*?JSESSIONID=(.+);.*', cookies, re.M | re.I)
        if match_obj is None:
            raise CloudstackAPIException("Login failed, no JSESSIONID cookie found in response")
        session_id = match_obj.group(1)
        return session_id

    def __login(self, details):
        url = details.baseUrl + '?login'
        payload = Struct(
            command='login',
            username=details.user,
            password=details.password,
            domain=details.domain
        )
        r = self.post(url, data=payload)
        session_id = self.__get_session_id(r)
        doc = ET.fromstring(r.text)
        session_key = doc.findtext('.//sessionkey')
        if session_key is None:
            raise CloudstackAPIException(
                "Login failed, no <sessionkey/> found in response")
        user_id = doc.findtext('.//userid')
        if user_id is None:
            raise CloudstackAPIException(
                "Login failed, no <userid/> found in response")

        session = dict(sessionId=session_id, sessionKey=session_key, userId=user_id,
                       cookies=dict(JSESSIONID=session_id))
        session = namedtuple('Session', session.keys())(*session.values())
        if TRACE:
            print "established session:"
            pprint.pprint(session)
        return session

    def __get_existing_api_keys(self, details, session):
        payload = Struct(
            command='listUsers',
            id=session.userId,
            sessionkey=session.sessionKey
        )
        if TRACE:
            pprint.pprint(payload)
        try:
            r = self.post(details.baseUrl, data=payload, cookies=session.cookies)
        except requests.HTTPError, e:
            if not hasattr(e, 'response'):
                raise
            response = e.response
            if not hasattr(response, 'status_code'):
                raise
            status_code = response.status_code
            if status_code == 401:
                print "__get_existing_api_keys() got 401 on listUsers, returning None"
                return None, None
            else:
                raise
        doc = ET.fromstring(r.text)
        api_key = doc.findtext('.//apikey')
        secret_key = doc.findtext('.//secretkey')
        return api_key, secret_key  # both can be None

    def __register_api_keys(self, details, session):
        payload = Struct(
            command='registerUserKeys',
            id=session.userId,
            sessionkey=session.sessionKey
        )
        if TRACE:
            pprint.pprint(payload)
        r = self.post(details.baseUrl, data=payload, cookies=session.cookies)
        doc = ET.fromstring(r.text)
        api_key = doc.findtext('.//apikey')
        secret_key = doc.findtext('.//secretkey')
        return api_key, secret_key  # both can be None

    def __find_api_keys(self, details):
        if details.apiKey is not None and details.securityKey is not None:
            return

        session = self.__login(details)
        api_key, secret_key = self.__get_existing_api_keys(details, session)
        if api_key is None or secret_key is None:
            api_key, secret_key = self.__register_api_keys(details, session)
            if api_key is None or secret_key is None:
                raise CloudstackAPIException(
                    "Key registration failed, no <apikey/> or <secretkey/> found in response")

        details.apiKey = api_key
        details.secretKey = secret_key
        details.securityKey = secret_key  # kill me now


class CloudStackAPIClient(MarvinCloudStackAPIClient):
    pass


class CloudStackObjectAPI(object):
    _connection = None
    _api_client = None
    _initialized = False

    @classmethod
    def init_connection(cls, **kwargs):
        if cls._initialized:
            return
        cls._initialized = True
        cls._connection = CSConnection(**kwargs)
        cls._api_client = CloudStackAPIClient(cls._connection)

    @classmethod
    def connection(cls):
        cls.init_connection()
        return cls._connection

    @classmethod
    def api_client(cls):
        cls.init_connection()
        return cls._api_client

    def __init__(self):
        self.init_connection()
