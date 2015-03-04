import feedparser
import urllib2
from bs4 import BeautifulSoup
from couchdb.client import Server, Document
from couchdb.mapping import TextField, DateTimeField, ListField
from uuid import uuid4

class collect_beer(Document):
    brewery  = TextField()
    venue = TextField()
    beer = TextField()

couch = Server('http://192.168.59.103:49153/')
dbv = couch['untappd_venue']
dbb = couch['untappd_beer']
venue_list = ["https://untappd.com/rss/venue/3538"]

for i in venue_list:
    feed = feedparser.parse(i)
    print feed
check_in = []
for i in range(len(feed['entries'])):
    e = collect_beer()
    e['_id'] = uuid4().hex
    e['venue'] = "Saraveza"
    print "Getting Untappd checkin:"
    print feed['entries'][i]['links'][0]['href']
    web_page = urllib2.urlopen(feed['entries'][i]['links'][0]['href'])
    soup = BeautifulSoup(web_page)
    c = soup.find_all("div", class_="beer")
    for div in c:
        checkin_data = div.find_all('a')
    for i in range(len(checkin_data)):
        if i % 2 == 0:
            e['beer'] = (checkin_data[i].get_text())
        else:
            e['brewery'] = (checkin_data[i].get_text())
    doc_id, doc_rev = dbv.save(e)
    print doc_id, doc_rev

for docid in dbv:
  e = dbv.get(docid)
  print e['brewery'], e['beer'], e['venue']

beer_query = "Pliny The Younger"
code = '''function(doc) { if(doc.beer == '%s') emit(doc.frm, null); }''' % beer_query
for res in dbv.query(code):
    g = dbv.get(res.id)
    print g['beer'] + " is at " + g['venue']


