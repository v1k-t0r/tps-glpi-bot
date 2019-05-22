"""Cisco ASA vpn clients list"""
import base64
import json
import sys
import urllib2
import logging
import time
import re
import ConfigParser
from functools import wraps
from telegram import constants
from telegram.ext import Updater, CommandHandler
from integrate import TestCase, test

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

"""
Uncomment the following lines,
if you are using Python 2.7.9 or above to connect to an ASA with a self-signed certificate.
"""
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
PARSER = ConfigParser.ConfigParser()
PARSER.read('config.ini')

IPADRESS = PARSER.get('options', 'ipaddress')
USERNAME = PARSER.get('options', 'username')
PASSWORD = PARSER.get('options', 'password')
PORT = PARSER.get('options', 'port')
BOT_ID = PARSER.get('options', 'bot_id')
LIST = PARSER.get('options', 'LIST')
GROUP1 = PARSER.get('options', 'group1')
GROUP2 = PARSER.get('options', 'group2')
if len(sys.argv) > 1:
    USERNAME = sys.argv[1]
if len(sys.argv) > 2:
    PASSWORD = sys.argv[2]
# Mgmt URL
SERVER = "https://" + IPADRESS + ":" + PORT
HEADERS = {'Content-Type': 'application/json'}

API_PATH = "/api/cli"    # param
URL = SERVER + API_PATH

class Test(TestCase):
    "test case"
    @test(skip_if_failed=["get_sessions_test"])
    def sessions_test(self, check):
        "sessions test"
        check.is_not_none(sessions, message=None)
    @test(skip_if_failed=["get_sessions_test"])
    def srv_test(self, check):
        "srv test"
        check.is_not_none(srv, message=None)
    @test()
    def get_sessions_test(self, check):
        "get_sessions test"
        check.is_not_none(get_sessions, message=None)

def restricted(func):
    """Restriction function"""
    @wraps(func)
    def wrapped(_bot, update):
        """wraper"""
        user_id = update.effective_user.id
        if str(user_id) not in LIST:
            update.message.reply_text("Unauthorized access denied.\n"
                                      "Please add {} in config.ini LIST variable".format(user_id))
            return user_id
        return func(_bot, update)
    return wrapped

@restricted
def start(_bot, update):
    """Start function"""
    update.message.reply_text("Commands:\n/srv\n/sessions")

def get_sessions():
    """Request to ASA API"""
    post_data = {"commands":
                 ["show vpn-sessiondb anyconnect | include Username|Assigned IP|Group Policy"]}
    req = urllib2.Request(URL, json.dumps(post_data), HEADERS)
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)
    try:
        con = urllib2.urlopen(req)
        status_code = con.getcode()
        print "Status code is "+str(status_code)
        resp = con.read()
        res = str('%s' % (resp)).replace('{"response":["',
                                         '').replace('"]}', '').replace('\\n', '\n')
        res0 = re.sub(r'\nGroup Policy\s+[:]\s\w+\s+\w+\s\w+', '', res)
        res0 = re.sub(r'[:]\s%s' % (GROUP1), '', res0)
        res1 = re.sub(r'Index\s+[:]\s\d+\n', '', res0)
        res2 = re.sub(r'Username\s+[:]\s', '', res1)
        res3 = re.sub(r'Assigned IP', '', res2)
        res4 = re.sub(r'Public IP', '', res3)
        response = re.sub(' +', ' ', res4)
        if status_code == 201:
            print "Create was successful"
    except urllib2.HTTPError, err:
        print "Error received from SERVER. HTTP Status code :"+str(err.code)
        try:
            json_error = json.loads(err.read())
            if json_error:
                print json.dumps(json_error, sort_keys=True, indent=4, separators=(',', ': '))
        except ValueError:
            pass
    finally:
        if con:
            con.close()
    return response

@restricted
def srv(_bot, update):
    """Search GROUP2 session and send to tg"""
    response = get_sessions()
    ses = ""
    for line in response.splitlines():
        if re.search(r'%s' % (GROUP2), line):
            ses = ses + "\n" + line
    count = ses.count('\n')
    ssrv = '\n'.join(sorted(ses.splitlines()))
    update.message.reply_text('%s\n*Connected: %d*' % (ssrv, count), parse_mode='markdown')

@restricted
def sessions(_bot, update):
    """Send sessions to tg"""
    response = get_sessions()
    response = '\n'.join(sorted(response.splitlines()))
    parts = []
    while response:
        if len(response) > constants.MAX_MESSAGE_LENGTH:
            part = response[:constants.MAX_MESSAGE_LENGTH]
            first_lnbr = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                response = response[first_lnbr:]
            else:
                parts.append(part)
                response = response[constants.MAX_MESSAGE_LENGTH:]
        else:
            parts.append(response)
            break
    count = response.count('\n')
    msg = None
    for part in parts:
        msg = update.message.reply_text('%s\n*Total: %d anyconnect sessions*' % (part, count),
                                        parse_mode='markdown')
        time.sleep(1)
    return msg  # return only the last message

def error_func(_bot, update, error):
    """error loging function"""
    LOGGER.warn("Update %s caused error %s", update, error)

def main():
    """TG updater function"""
    updater = Updater(BOT_ID)
    dsp = updater.dispatcher
    dsp.add_handler(CommandHandler("start", start))
    dsp.add_handler(CommandHandler("sessions", sessions))
    dsp.add_handler(CommandHandler("srv", srv))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
