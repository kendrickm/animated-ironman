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
from barfight import add_checkin, add_review
import config


app = Flask(__name__)


docs_beer = ViewDefinition('docs', 'beer',
                                'function(doc) { emit(doc.beer, doc);}')
docs_venue = ViewDefinition('docs', 'venue',
                                'function(doc) { emit(doc.venue, doc);}')

@app.route('/checkin', methods=['POST'])
@app.route('/checkin/<source_type>', methods=['POST'])
def new_checkin(source_type="raw"):
    data = request.json['data']
    source_id = request.json['source_id']
    dryrun = False
    if source_id == 'dryrun':
        dryrun = True
    if source_type == 'raw':
        source = "raw"
    else:
        source = request.json['source']
    date = request.json['date']
    try:
        venue_id = request.json['venue']
        ven_name = "unknown"
    except KeyError:
        venue = reverse_lookup(source_type, source) #TODO Handle a location that doesn't exist
        venue_id = venue['_id']
        ven_name = venue['name']

    if not dryrun and source_type != "raw":
        update_last_scraped(source_type, source, source_id)

    if request.json['needs_review']:
        if add_review(data, date, source_type, source_id, venue_id):
            return "created a review item", 200
        else:
            return "An error occured", 500


    #TODO Convert all this to an object
    beer_id = brewerydb_full_search(data)
    if not beer_id:
        if add_review(data, date, source_type, source_id, venue_id):
            print "Unable to find beer with data: %s" % (data)
            return "Unable to find beer information. Saving this for a manual review", 200
        else:
            return "An error occured", 500
    beer = beer_lookup(beer_id)
    brewery = brewery_lookup_by_beer(beer_id)
    print "Storing a checkin from source_type %s with source_id of %s" % (source_type, source_id)
    print "Checking in to %s with beer %s by brewery %s at %s" % (ven_name, beer['name'], brewery['name'], date)
    if not dryrun:
        if add_checkin(beer['name'], brewery['name'], date, source_type, source_id, venue_id):
            return "created", 201
        else:
            return "An error occured", 500

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
      ids = lookup('twitter', "last_scraped.twitter")
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
manager.setup(app)
manager.add_viewdef(docs_beer)  # Install the view
manager.add_viewdef(docs_venue)  # Install the view
manager.sync(app)
app.run(host='0.0.0.0', port=5000)
