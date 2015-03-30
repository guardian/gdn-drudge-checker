#!/usr/bin/env python
from google.appengine.ext import db

class Records(db.Model):
  storyUrl            = db.StringProperty()
  apiUrl              = db.StringProperty()
  reason              = db.StringProperty(default='')
  headline            = db.StringProperty(default='')
  json                = db.TextProperty()
  processed           = db.IntegerProperty(default=0)
  emailed             = db.IntegerProperty(default=0)
  valid               = db.IntegerProperty(default=1)
  wordpressed         = db.IntegerProperty(default=0)
  wordpress_checked   = db.IntegerProperty(default=0)
  backfilled          = db.IntegerProperty(default=0)
  first_seen          = db.DateTimeProperty(auto_now_add=True, required=True)
  last_seen           = db.DateTimeProperty(auto_now_add=True, required=True)