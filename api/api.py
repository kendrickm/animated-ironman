#!/usr/bin/python
import simplejson
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import flaskext.couchdb
import yaml

with open('db.yaml', 'r') as f:
    db = yaml.load(f)

app = Flask(__name__)

docs_beer = ViewDefinition('docs', 'beer',
                                'function(doc) { emit(doc.beer, doc);}')

docs_venue = ViewDefinition('docs', 'venue',
                                'function(doc) { emit(doc.venue, doc);}')


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
        COUCHDB_SERVER = db["db_config"]["COUCHDB_SERVER"],
        COUCHDB_DATABASE = db["db_config"]["COUCHDB_DATABASE"]
)

#if __name__ == "__main__":
manager = flaskext.couchdb.CouchDBManager()
manager.setup(app)
manager.add_viewdef(docs_beer)  # Install the view
manager.add_viewdef(docs_venue)  # Install the view
manager.sync(app)
app.run(host='0.0.0.0', port=5000)
