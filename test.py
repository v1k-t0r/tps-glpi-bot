from integrate import TestCase, test
#import ses
import urllib2
import ConfigParser
import json
import base64

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

PARSER = ConfigParser.ConfigParser()
PARSER.read('config.ini')

IPADRESS = PARSER.get('options', 'ipaddress')
USERNAME = PARSER.get('options', 'username')
PASSWORD = PARSER.get('options', 'password')
PORT = PARSER.get('options', 'port')
LIST = PARSER.get('options', 'LIST')
GROUP1 = PARSER.get('options', 'group1')
GROUP2 = PARSER.get('options', 'group2')
# Mgmt URL
SERVER = "https://" + IPADRESS + ":" + PORT
HEADERS = {'Content-Type': 'application/json'}

API_PATH = "/api/cli"    # param
URL = SERVER + API_PATH

class Test(TestCase):
    "ASA API availability test case"

    @test()
    def asa_con_test(self, check):
        """test request to ASA API"""
        post_data = {"commands":
                     ["show vpn-sessiondb anyconnect | include Username|Assigned IP|Group Policy"]}
        req = urllib2.Request(URL, json.dumps(post_data), HEADERS)
        base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        self.con = urllib2.urlopen(req)
        status_code = self.con.getcode()
        check.equal(str(status_code), '200')

    @test(skip_if_failed=["asa_con_test"])
    def asa_api_test1(self, check):
        """test1 request to ASA API"""
        resp = self.con.read()
        check.is_not_none(resp, message=None)
