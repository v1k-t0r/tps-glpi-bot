#
# Generated ASA REST API sample script - Python 2.7
#
import base64
import json
import sys
import urllib2
import pyjq
import logging
import time
import re
import ConfigParser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, constants
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler, BaseFilter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Uncomment the following two lines, if you are using Python 2.7.9 or above to connect to an ASA with a self-signed certificate.
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
parser = ConfigParser.ConfigParser()
parser.read('config.ini')

ipaddress = parser.get('options', 'ipaddress')
username = parser.get('options', 'username')
password = parser.get('options', 'password')
port = parser.get('options', 'port')
bot_id = parser.get('options', 'bot_id')
if len(sys.argv) > 1:
    username = sys.argv[1]
if len(sys.argv) > 2:
    password = sys.argv[2]
# Mgmt url
server = "https://" + ipaddress + ":" + port
headers = {'Content-Type': 'application/json'}

api_path = "/api/cli"    # param
url = server + api_path
f = None

def help(bot, update):
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
        update.message.reply_text(user_id)

def sessions(bot,update):
    post_data = {
      "commands": [
          "show vpn-sessiondb anyconnect | include Username|Assigned IP|Group Policy"
	  ]
	}
    req = urllib2.Request(url, json.dumps(post_data), headers)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)   
    try:
        f  = urllib2.urlopen(req)
        status_code = f.getcode()
        print "Status code is "+str(status_code)
        resp = f.read()
        r = str('%s' % (resp)).replace('{"response":["' ,'').replace('"]}', '').replace('\\n', '\n')
        r0 = re.sub(r'\nGroup Policy\s+[:]\s\w+\s+\w+\s\w+', '', r)
        r0 = re.sub(r'[:]\sasavpn', '', r0)
        r1 = re.sub(r'Index\s+[:]\s\d+\n', '', r0)
        r2 = re.sub(r'Username\s+[:]\s', '', r1)
        r3 = re.sub(r'Assigned IP', '', r2)
        r4 = re.sub(r'Public IP', '', r3)
        r5 = re.sub(' +', ' ', r4)
        parts = []
        while len(r5) > 0:
            if len(r5) > constants.MAX_MESSAGE_LENGTH:
                part = r5[:constants.MAX_MESSAGE_LENGTH]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    r5 = r5[first_lnbr:]
                else:
                    parts.append(part)
                    r5 = r5[constants.MAX_MESSAGE_LENGTH:]
            else:
                parts.append(r5)
                break

        msg = None
        for part in parts:
            msg = update.message.reply_text(part)
            time.sleep(1)
        return msg  # return only the last message
        if status_code == 201:
            print "Create was successful"
    except urllib2.HTTPError, err:
        print "Error received from server. HTTP Status code :"+str(err.code)
        try:
            json_error = json.loads(err.read())
            if json_error:
                print json.dumps(json_error,sort_keys=True,indent=4, separators=(',', ': '))
        except ValueError:
            pass
    finally:
        if f:  f.close()

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    updater = Updater(bot_id)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("sessions", sessions))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
