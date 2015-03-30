#!/usr/bin/env python
import os
import sys
import logging

from thetools.seo.admin.models import Records
from admin.BeautifulSoup import BeautifulSoup
import json
from datetime import date, datetime
from google.appengine.ext import db
from google.appengine.api import urlfetch

print 'Content-Type: text/html; charset=UTF-8'
print ''


#
# Ok, so this is annoying and daft *but* I want to keep passwords out of github
# which isn't really a problem, but there's also one unpublished URL that I
# can't make public *yet*
#
# When that URL is public, I'll clean this up to give a developer a better way
# of adding their own Wordpress and Guardian APIs and so on.
#
try:
  import passwords
except Exception:
  print 'application is missing the passwords file'
  sys.exit()


################################################################################
################################################################################
#
# End of messy include stuff
#
################################################################################
################################################################################



fetch_url = 'http://www.drudgereport.com/'
result = urlfetch.fetch(url=fetch_url)

search = {
  'match': 'theguardian.com',
  'root': 'http://www.theguardian.com/',
}


results = []

if result.status_code != 200:
  print ''
  print 'failed with code != 200'
  sys.exit()
  

# Now we want to find all the links in the document
soup = BeautifulSoup(result.content)

links = soup.findAll('a')

for link in links:


  # If the thing we are searching for is in the href, but it's the href itself, then we have a link
  # to the site we are looking for

  if search['match'] in link['href'] and link['href'] != search['root']:
    
    # Build a simple object to hold the URL and the title
    try:
      result_obj =  {
        'link': link['href'].split('?')[0],
        'headline': ' '.join(link.contents[0].findAll(text=True))
      }
      results.append(result_obj);
    except:
      try:
        headline = str(link).split('">')[1].split('</a>')[0]
        result_obj =  {
          'link': link['href'].split('?')[0],
          'headline': headline
        }
        results.append(result_obj);
      except:
        logging.debug('MONITOR_DRUDGE: LINK FAIL: %s' % link)
  

# Now that we have a list of links and headlines let's check to see if we already
# have them
print ''
for result in results:
  print result
  g_link = str(result['link'])
  g_headline = str(result['headline'])
  rows = db.GqlQuery("SELECT * FROM Records WHERE storyUrl = :1", g_link)


  if rows.count() != 0:
    print 'already have row'
    for row in rows:
      row.last_seen = datetime.now();
      row.put()
    continue
  
  # Now we know there isn't a match we need to see if we can resolve it to
  # an API
  logging.debug(g_link)
  fetch_url = g_link.replace('http://www.theguardian.com', passwords.content_api_host()) + '?format=json&show-fields=all&show-tags=all&api-key=' + passwords.guardian_api_key()
  result = urlfetch.fetch(url=fetch_url)
  
  if result.status_code != 200:
    new_row                  = Records()
    new_row.storyUrl         = g_link
    new_row.reason           = 'Drudge'
    new_row.headline         = g_headline
    new_row.valid            = 0
    new_row.put()
    continue

  # Now check that we can get the URL out
  
  try:
    guardian_json = json.loads(result.content)
  except Exception:
    print 'couldn\'t convert guardian to json'
    new_row                  = Records()
    new_row.storyUrl         = g_link
    new_row.reason           = 'Drudge'
    new_row.headline         = g_headline
    new_row.valid            = 0
    continue


  # But we now have a resolved URL, we once more need to check to see if we already
  # have this item
  logging.debug(guardian_json)

  if not 'content' in guardian_json['response']:
    continue

  webUrl = guardian_json['response']['content']['webUrl']

  rows = db.GqlQuery("SELECT * FROM Records WHERE storyUrl = :1", webUrl)
  
  if rows.count() != 0:    
    # if the old url was different to the resolved url then
    # mark the old url as invalid
    if webUrl != g_link:
      print 'already have record, in a different form'
      new_row                  = Records()
      new_row.storyUrl         = g_link
      new_row.reason           = 'Drudge'
      new_row.headline         = g_headline
      new_row.valid            = 0
      new_row.put()
    else:
      print 'mark new most recent seen time'
      for row in rows:
        row.last_seen = datetime.now();
        row.put()

    continue

  # Add it as a new record
  try:
    new_row                  = Records()
    new_row.storyUrl         = g_link
    new_row.apiUrl           = guardian_json['response']['content']['apiUrl']
    new_row.reason           = 'Drudge'
    new_row.headline         = guardian_json['response']['content']['webTitle']
    new_row.json             = json.dumps(guardian_json)
    new_row.processed        = 1
    new_row.put()
  except Exception:
    logging.debug('DATABASE: something went wrong putting it into the database')

print 'done!'