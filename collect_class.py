import feedparser
import urllib2
from bs4 import BeautifulSoup
from couchdb.client import Server, Document
from couchdb.mapping import TextField, DateTimeField, ListField
from uuid import uuid4

class untappd_collect:
    def __init__(self,location):
        '''
        This is some shit.
        '''
        self.location = location
        #self.taplist = ""
    def populate_taplist(self,current_feed):
        for i in range(len(current_feed['entries'])):
            e = collect_beer()
            e['_id'] = uuid4().hex
            e['venue'] = self.location
            print "Getting Untappd checkin:"
            print current_feed['entries'][i]['links'][0]['href']
            web_page = urllib2.urlopen(current_feed['entries'][i]['links'][0]['href'])
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

class collect_beer(Document):
    brewery  = TextField()
    venue = TextField()
    beer = TextField()

venue_list = {"Troutdale House": "https://untappd.com/rss/venue/426211", "Saraveza": "https://untappd.com/rss/venue/3538"}

couch = Server('http://192.168.59.103:49153/')
dbv = couch['untappd_venue']
dbb = couch['untappd_beer']

feed = []

for value in venue_list.itervalues():
    feed.append(feedparser.parse(value))
    print feed
for rss, data in zip(venue_list.iterkeys(), feed):
    venue = untappd_collect(rss)
    venue.populate_taplist(data)

