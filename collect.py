import dbinteract
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
venue_name = ["Saraveza"]

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
    #print web_page
#grab timestamp?
    soup = BeautifulSoup(web_page)
    c = soup.find_all("div", class_="beer")
    for div in c:
        poop = div.find_all('a')
    for i in range(len(poop)):
        if i % 2 == 0:
            e['beer'] = (poop[i].get_text())
        else:
            e['brewery'] = (poop[i].get_text())
    doc_id, doc_rev = dbv.save(e)
    print doc_id, doc_rev

for docid in dbv:
  e = dbv.get(docid)
  print e['brewery'], e['beer'], e['venue']
