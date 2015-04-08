#!/usr/bin/python
import simplejson
import foursquare
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import couchdb
from foursquare import ParamError
import flaskext.couchdb
import yaml
from location import *
from brewerydb import brewerydb_full_search, beer_lookup, brewery_lookup_by_beer
import config


app = Flask(__name__)


docs_beer = ViewDefinition('docs', 'beer',
                                'function(doc) { emit(doc.beer, doc);}')
docs_venue = ViewDefinition('docs', 'venue',
                                'function(doc) { emit(doc.venue, doc);}')


@app.route('/checkin/<source_type>', methods=['POST'])
def new_checkin(source_type):
    # print request.json
    if request.json['needs_review']:
        print "Saving this request until a review can be made"
        return "created", 202
    data = request.json['data']
    source_id = request.json['source_id']
    source = request.json['source']
    date = request.json['date']

    venue = reverse_lookup(source_type, source) #TODO Handle a location that doesn't exist
    #TODO Convert all this to an object
    beer_id = brewerydb_full_search(data)
    beer = beer_lookup(beer_id)
    brewery = brewery_lookup_by_beer(beer_id)

    print "Storing a checkin from source_type %s with source_id of %s" % (source_type, source_id)
    print "Checking in to %s with beer %s by brewery %s at %s" % (venue['name'], beer['name'], brewery['name'], date)
    return "created", 201

#Accepts a foursqure id and populates the
#location database with the information
@app.route('/location/<venue>', methods=['POST'])
def location_venue(venue):
  return add_venue(venue)

#Accepts a foursqure id and the untappd location id and populates the
#location database with the information
@app.route('/location/<venue>/<untappd>', methods=['POST'])
def location_venue_untappd(venue, untappd):
  return add_venue(venue, untappd)


@app.route('/locations')
def location_lookup():
  if request.args.get('type') == "untappd":
      ids = lookup('untappd_id')
  elif request.args.get('type') == "twitter":
      ids = lookup('twitter')
  elif request.args.get('type') == "facebook":
      ids = lookup('fb_id')
  else:
      return "Not yet implemented"

  results = {
    "search_results":ids
  }
  return simplejson.dumps(results)

@app.route("/beer/<id>")
def get_beer(id):
    docs = []
    for row in docs_beer(g.couch)[id]:
        docs.append(row.value)
    return simplejson.dumps(docs)

@app.route("/venue/<id>")
def get_location(id):
    docs = []
    for row in docs_venue(g.couch)[id]:
        docs.append(row.value)
    return simplejson.dumps(docs)

@app.route("/untappd/add", methods=['POST'])
def add_doc():
    try:
        doc = {
        'beer': request.json['beer'],
        'brewery': request.json['brewery'],
        'venue': request.json['venue']
        }
        #doc.update(request.json)
        g.couch.save(doc)
        state = True
    except Exception, e:
        state = False
    return simplejson.dumps({'ok': state})

app.config.update(
        DEBUG = True,
        COUCHDB_SERVER = config.db_config["COUCHDB_SERVER"],
        COUCHDB_DATABASE = config.db_config["COUCHDB_DATABASE"]
)

#if __name__ == "__main__":
manager = flaskext.couchdb.CouchDBManager()
loc_manager = flaskext.couchdb.CouchDBManager()
manager.setup(app)
manager.add_viewdef(docs_beer)  # Install the view
manager.add_viewdef(docs_venue)  # Install the view
manager.sync(app)
app.run(host='0.0.0.0', port=5000)
