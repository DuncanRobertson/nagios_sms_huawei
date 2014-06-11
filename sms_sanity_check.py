#!/usr/bin/python
#
#
# simpified  reimplementation of SMS_client using 3G dongle.. 10 times faster!!
#
# needs http://code.google.com/p/pyhumod/
#
# and an uptodate version of usb-modeswitch to do all the USB dongle bizness
#
# this is a regular check that the SMS system is working.. a cron job sends an expected string,
# then we check that the expected string is there. alert if not.
#
# printf "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostr" | /usr/admin/custom_nagios_plugins/sms_client_huawei.py  telstra:smsnumber
#
#

SANITY = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostr"

FOUNDSANITY = False

# Pin of SIM card
PIN = 1234
# modem model
MODEMMODEL = 'E122'

import humod, sys, string, lockfile

lock = lockfile.FileLock("/tmp/sms_client_huawei")

if lock.is_locked():
   print "modem locked, so we will wait..."
lock.acquire()


m=humod.Modem()

if m.get_pin_status()  == 'SIM PIN':
   m.enter_pin(PIN)

if m.show_model() != MODEMMODEL:
   print "didnt find 3G modem model ",MODEMMODEL," instead found ",m.show_model()
   lock.release()
   sys.exit(1)
else:
   print "3G modem model found as E122"

#
# We go through the SMS list and check for ones matching the SANITY string, which we delete
#

m.enable_textmode(True)
messages = m.sms_list()
for message in messages:
   contents =  m.sms_read(message[0])
   # print contents
   if contents == SANITY:
      FOUNDSANITY = True
      m.sms_del(message[0])
   else:
      print
      print "got SMS that isn't the sanity check, here it is before we delete it:"
      print message
      print contents
      print
      m.sms_del(message[0])

if FOUNDSANITY:
   print "SMS Sanity Check Passed"
   lock.release()
   sys.exit(0)
else:
   print "SMS Sanity Check Failed"
   print " note: often unplugging the 3G dongle for 15 seconds will fix this."
   lock.release()
   sys.exit(1)

