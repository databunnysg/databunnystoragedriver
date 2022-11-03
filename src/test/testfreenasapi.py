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
#sys.path.append(os.path.abspath(".."))
# os.chdir(os.path.abspath("../.."))
import configparser
from driver import utils as ix_utils
config = configparser.ConfigParser()
    
def createvolume(name,size):
    name,size=("test",1)
    freenas = FreeNASServer(config['cinder-databunny-driver']['ixsystems_server_hostname']
                            ,config['cinder-databunny-driver']['ixsystems_server_port']
                                    ,config['cinder-databunny-driver']['ixsystems_login']
                                    ,config['cinder-databunny-driver']['ixsystems_password'])
    params = {}
    params['name'] = config['cinder-databunny-driver']['ixsystems_dataset_path'] + '/' + name
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
    freenas = FreeNASServer(config['cinder-databunny-driver']['ixsystems_server_hostname']
                            ,config['cinder-databunny-driver']['ixsystems_server_port']
                                    ,config['cinder-databunny-driver']['ixsystems_login']
                                    ,config['cinder-databunny-driver']['ixsystems_password'])
    request_urn = ('%s/id/%s%s') % (
        FreeNASServer.REST_API_VOLUME,
        urllib.parse.quote_plus(
            config['cinder-databunny-driver']['ixsystems_dataset_path'] + '/'),
        name)
    ret = freenas.invoke_command(FreeNASServer.DELETE_COMMAND,
                                        request_urn, None)

    if ret['status'] != FreeNASServer.STATUS_OK:
        msg = ('Error while creating volume: %s' % ret['response'])
        raise FreeNASApiError('Unexpected error', msg)
    return True
def update_volume_stats():
        """Retrieve stats info from volume group.

           REST API: $ GET /pools/mypool "size":95,"allocated":85,
        """
        # HACK: for now, use an API v1.0 call to get
        # these stats until available in v2.0 API
        freenas = FreeNASServer(config['cinder-databunny-driver']['ixsystems_server_hostname']
                            ,config['cinder-databunny-driver']['ixsystems_server_port']
                                    ,config['cinder-databunny-driver']['ixsystems_login']
                                    ,config['cinder-databunny-driver']['ixsystems_password'])
        #freenas.set_api_version('v2.0')
        #for api v1.0
        #request_urn = ('%s/%s/') % (
        #    '/storage/volume',
        #    config['cinder-databunny-driver']['ixsystems_datastore_pool'])
        
        #for api v2.0
        request_urn = ('%s') % ('/pool')
        config['cinder-databunny-driver']['ixsystems_datastore_pool']
        ret = freenas.invoke_command(FreeNASServer.SELECT_COMMAND,
                                         request_urn, None)
        retresult = json.loads(ret['response'])
        for retitem in retresult:
            if retitem['name']==config['cinder-databunny-driver']['ixsystems_datastore_pool']:
                size= retitem['topology']['data'][0]['stats']['size']
                used = retitem['topology']['data'][0]['stats']['allocated']
                print("avail"+str(size))
                print("used"+str(used))
                                   
        data = {}
        #avail = json.loads(ret['response'])['avail']
        #used = json.loads(ret['response'])['used']
        data["volume_backend_name"] = config['cinder-databunny-driver']['ixsystems_volume_backend_name']
        data["vendor_name"] = config['cinder-databunny-driver']['ixsystems_vendor_name']
        data["driver_version"] = config['cinder-databunny-driver']['ixsystems_api_version']
        data["storage_protocol"] = config['cinder-databunny-driver']['ixsystems_storage_protocol']
        data['total_capacity_gb'] = ix_utils.get_size_in_gb(size)
        data['free_capacity_gb'] = ix_utils.get_size_in_gb(used)
        data['reserved_percentage'] = (
            config['cinder-databunny-driver']['ixsystems_reserved_percentage'])
        data['reserved_percentage'] = 0
        data['QoS_support'] = False

        # set back to v2.0 api for other calls...
        #freenas.set_api_version('v2.0')
        return data
class testfreenasapi(unittest.TestCase):
    def testcreatevolumefreenas(self):
        global config
        config.read("./src/test/cindertruenas13.conf")    
        assert createvolume("test",1)
    def testdelvolumefreenas(self):
        global config
        config.read("./src/test/cindertruenas13.conf")    
        assert delvolume("test")    
    def testcreatevolumetruenasscale(self):
        global config
        config.read("./src/test/cindertruenasscale.conf")    
        assert createvolume("test",1)
    def testdelvolumetruenasscale(self):
        global config
        config.read("./src/test/cindertruenasscale.conf")    
        assert delvolume("test")     
    def testtruenassstats(self):
        global config
        config.read("./src/test/cindertruenas13.conf")    
        assert update_volume_stats()               
    def testtruenassscalestats(self):
        global config
        config.read("./src/test/cindertruenasscale.conf")            
        assert update_volume_stats()
        
if __name__ == '__main__':
    unittest.main()