#!/usr/bin/python
#
# needs http://code.google.com/p/pyhumod/
#
# and an uptodate version of usb-modeswitch to do all the USB dongle bizness
#
# very quick test that the modem is returning a model number, nonintrusive test that
# the device is at least hooked up.
#
# see sms_sanity_check.py for a complete check of SMS functionality by sending an SMS and checking it is received.
#
# Pin of SIM card
PIN = 1234
MODEMMODEL = 'E122'

TIMEOUT=120

import humod, sys, string, lockfile

lock = lockfile.FileLock("/tmp/sms_client_huawei")

if lock.is_locked():
   print "modem locked, so we will wait..."

try:
   lock.acquire(timeout=TIMEOUT)
except lockfile.LockTimeout:
   print "couldn't acquire lock on modem in within timeout ",TIMEOUT," seconds."
   sys.exit(2)

errcode = 0
try:
   m=humod.Modem()

   if m.get_pin_status()  == 'SIM PIN':
      m.enter_pin(PIN)

   foundmodel = m.show_model()
   if foundmodel != MODEMMODEL:
      print "detected modem model: " ,foundmodel," not expected model: ",MODEMMODEL
      errcode = 2
   else:
      print "3G modem model found as Huawei ",foundmodel
except Exception, e:
   print "error running 3g modem check script:", e
   errcode = 2

lock.release()
sys.exit(errcode)
