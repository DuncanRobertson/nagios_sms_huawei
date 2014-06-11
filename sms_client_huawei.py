#!/usr/bin/python
#
# simpified reimplementation of SMS_client using 3G dongle.. 10 times faster than analogue modem!!
#
# requires http://code.google.com/p/pyhumod/
#
# and an uptodate version of usb-modeswitch to do all the USB dongle bizness
#

######################
# Pin of SIM card
PIN = 1234
fromemail = "root@email.com"
toemail = "sysadmins@email.com"

import humod, sys, string, lockfile, syslog, smtplib

debug = True

def sdebug(message):
   if debug:
      syslog.syslog(message)

lock = lockfile.FileLock("/tmp/sms_client_huawei")

if lock.is_locked():
   print "modem locked, so we will wait..."
   sdebug("modem locked, so we will wait...")
lock.acquire()
sdebug("lock acquired")

# we strip off the telstra string as that may be fed in by nagios as sms_client expects it.

number = sys.argv[1].lstrip("telstra:")

message = string.join(sys.stdin.readlines())

sdebug("number is "+number)
sdebug("message is "+' '.join(message))

m=humod.Modem()

if m.get_pin_status()  == 'SIM PIN':
   sdebug("had to enter pin")
   m.enter_pin(PIN)

sdebug("message length is "+str(len(message)))

# remove backslash, some some reason this appears to have started confusing the SMS system ????
message = message.replace("\\","")

# and square brackets!
message = message.replace("[","(")
message = message.replace("]",")")
# in fact there is a while pile of character set issues needed to be worked through if we can find
# out how.

message = message[:160]

tries = 5
sent = False
while tries > 0 and sent == False:
   m.enable_textmode(True)
   print "SMS send attempt..."
   sdebug("SMS send tries left "+str(tries))
   try:
      m.sms_send(number,message)
      sdebug("SENT")
      sent = True
   except Exception, e:
      # 
      print "ERROR SENDING SMS"
      failedreason = str(e)
      sdebug("ERROR SENDING SMS")
      tries = tries - 1

if sent == False:
   sdebug("GIVING UP")
   print "GIVING UP"
   # at least email somebody so we might know why the SMS didnt happen, and that one was attempted to be sent...
   print "last reason for failure was",failedreason
   sdebug("last reason for failure was "+failedreason)
   emailtext = """From: %s 
To: %s
Subject: error sending SMS from server
SMS text we were attempting to send: %s
Number sending to: %s
Reason for failing to send: %s

""" % (fromemail,toemail,message,str(number),failedreason)

   try:
      smtpObj = smtplib.SMTP('localhost')
      smtpObj.sendmail(fromemail, [toemail], emailtext)
   except:
      print "Error: unable to send email to "

   lock.release()
   sys.exit(1)

lock.release()
sys.exit(0)
