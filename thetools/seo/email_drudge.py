#!/usr/bin/env python
import os
import sys
import logging

from thetools.seo.admin.models import Records
from datetime import date, datetime
from google.appengine.ext import db
from google.appengine.api import mail

print 'Content-Type: text/html; charset=UTF-8'
print ''

rows = db.GqlQuery("SELECT * FROM Records WHERE emailed = 0 LIMIT 1")

if rows.count() == 0:
  logging.info('no more unprocessed rows')

if rows.count() > 0:

	email_row = rows[0]

	#print email_row.headline
	logging.debug(rows.count())


	message = mail.EmailMessage(sender=passwords.email()['from'],
	                            subject="DRUDGE: " + email_row.headline)
	message.to = passwords.email()['drudge_to']
	message.body = "This article " + email_row.storyUrl + " has been Drudged. It's important to make sure it is correctly packaged with related content (or content that may appeal to a US audience) and for moderators to be aware that the comment thread may need to be watched carefully."
	message.body += "\n\n"
	message.body += "(this is an automated message - reverse the polarity of the neutron flow)"

	message.send()

	email_row.emailed = 1
	email_row.put()
