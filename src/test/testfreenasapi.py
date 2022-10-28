# Copyright (c) Databunny Pte Ltd
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from driver.freenasapi import FreeNASServer
from driver.freenasapi import FreeNASApiError
import unittest
import json
import os,sys
import urllib.parse
sys.path.append(os.path.abspath(".."))
#sys.path.append(os.path.abspath("./test"))
import configparser
from driver import utils as ix_utils
config = configparser.ConfigParser()
config.read("./src/test/cinder.conf")        
def createvolume(name,size):
    name,size=("test",1)
    freenas = FreeNASServer(config['ixsystems-iscsi']['ixsystems_server_hostname']
                            ,config['ixsystems-iscsi']['ixsystems_server_port']
                                    ,config['ixsystems-iscsi']['ixsystems_login']
                                    ,config['ixsystems-iscsi']['ixsystems_password'])
    params = {}
    params['name'] = config['ixsystems-iscsi']['ixsystems_dataset_path'] + '/' + name
    params['type'] = 'VOLUME'
    params['volsize'] = ix_utils.get_bytes_from_gb(size)
    jparams = json.dumps(params)
    jparams = jparams.encode('utf8')
    request_urn = ('%s') % (FreeNASServer.REST_API_VOLUME)
    ret = freenas.invoke_command(FreeNASServer.CREATE_COMMAND,
                                        request_urn, jparams)

    if ret['status'] != FreeNASServer.STATUS_OK:
        msg = ('Error while creating volume: %s' % ret['response'])
        raise FreeNASApiError('Unexpected error', msg)
    return True
def delvolume(name):
    name,size=("test",1)
    freenas = FreeNASServer(config['ixsystems-iscsi']['ixsystems_server_hostname']
                            ,config['ixsystems-iscsi']['ixsystems_server_port']
                                    ,config['ixsystems-iscsi']['ixsystems_login']
                                    ,config['ixsystems-iscsi']['ixsystems_password'])
    request_urn = ('%s/id/%s%s') % (
        FreeNASServer.REST_API_VOLUME,
        urllib.parse.quote_plus(
            config['ixsystems-iscsi']['ixsystems_dataset_path'] + '/'),
        name)
    ret = freenas.invoke_command(FreeNASServer.DELETE_COMMAND,
                                        request_urn, None)

    if ret['status'] != FreeNASServer.STATUS_OK:
        msg = ('Error while creating volume: %s' % ret['response'])
        raise FreeNASApiError('Unexpected error', msg)
    return True
class testfreenasapi(unittest.TestCase):
    def testcreatevolume(self):
        assert createvolume("test",1)
    def testdelvolume(self):
        assert delvolume("test")    
        
if __name__ == '__main__':
    unittest.main()