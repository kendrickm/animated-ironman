#!/usr/bin/python
import simplejson
import foursquare
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import couchdb
from foursquare import ParamError
import flaskext.couchdb
import yaml
from location import lookup_venue, lookup_untappd, lookup_twitter, lookup_facebook
import config


app = Flask(__name__)


docs_beer = ViewDefinition('docs', 'beer',
                                'function(doc) { emit(doc.beer, doc);}')
docs_venue = ViewDefinition('docs', 'venue',
                                'function(doc) { emit(doc.venue, doc);}')


#Accepts a foursqure id and populates the
#location database with the information
@app.route('/location/<venue>', methods=['POST'])
def location_venue(venue):
  return lookup_venue(venue)

#Accepts a foursqure id and the untappd location id and populates the
#location database with the information
@app.route('/location/<venue>/<untappd>', methods=['POST'])
def location_venue_untappd(venue, untappd):
  return lookup_venue(venue, untappd)

@app.route('/locations')
def location_lookup():
  if request.args.get('type') == "untappd":
      return  simplejson.dumps(lookup_untappd())
  if request.args.get('type') == "twitter":
      return  simplejson.dumps(lookup_twitter())
  if request.args.get('type') == "facebook":
      return  simplejson.dumps(lookup_facebook())
  else:
      return "Not yet implemented"

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
