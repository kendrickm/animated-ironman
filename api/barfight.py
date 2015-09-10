import couchdb
import config
import simplejson
from flask import jsonify

server = couchdb.client.Server(url=config.db_config['COUCHDB_SERVER'])
bf_db = server[config.db_config['COUCHDB_DATABASE']]
nr_db = server[config.db_config['COUCHDB_DATABASE_REVIEW']]

def add_checkin( beer, brewery, date, source, source_id, venue):
    doc = {
        'beer': beer,
        'brewery': brewery,
        'date': date,
        'source': source,
        'source_id': source_id,
        'venue': venue
    }
    bf_db.save(doc)
    return 0

def add_review(data, date, source, source_id, venue):
    doc = {
        'data': data,
        'date': date,
        'source': source,
        'source_id': source_id,
        'venue': venue
    }
    nr_db.save(doc)
    return 0
