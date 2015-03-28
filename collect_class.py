import feedparser
import urllib2
from bs4 import BeautifulSoup
from couchdb.client import Server, Document
from couchdb.mapping import TextField, DateTimeField, ListField
from uuid import uuid4
import json

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
            #e['_id'] = uuid4().hex
            e['venue'] = self.location
            print "Getting Untappd checkin:"
            print current_feed['entries'][i]['links'][0]['href']
            web_page = urllib2.urlopen(current_feed['entries'][i]['links'][0]['href'])
            soup = BeautifulSoup(web_page)
            c = soup.find_all("div", class_="beer")
            #e['timestamp'] = soup.find("p", class_="time").string
            for div in c:
                checkin_data = div.find_all('a')
            for i in range(len(checkin_data)):
                if i % 2 == 0:
                    e['beer'] = (checkin_data[i].get_text())
                else:
                    e['brewery'] = (checkin_data[i].get_text())
            #duplicate checking
            req = urllib2.Request('http://127.0.0.1:5000/untappd/add')
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(e))
            print response
            #doc_id, doc_rev = dbv.save(e)

class collect_beer(Document):
    brewery  = TextField()
    venue = TextField()
    beer = TextField()

venue_list = {"Saraveza": "https://untappd.com/rss/venue/3538"}

feed = []

for value in venue_list.itervalues():
    feed.append(feedparser.parse(value))
    print feed
for rss, data in zip(venue_list.iterkeys(), feed):
    venue = untappd_collect(rss)
    venue.populate_taplist(data)
