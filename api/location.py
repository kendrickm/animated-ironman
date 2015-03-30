import couchdb
import config
import foursquare
import simplejson

def lookup_venue(venue, untappd=None):

    server = couchdb.client.Server(url=config.db_config['COUCHDB_SERVER'])
    loc_db = server['locations']
    try:
      client = foursquare.Foursquare(client_id=config.fsq_config['CLIENT_ID'],
      client_secret=config.fsq_config['CLIENT_SECRET'], version=config.fsq_config['API_VERSION'])

      v_data  = client.venues(venue)['venue']
      name    = v_data['name']
      twitter = v_data['contact']['twitter']
      fb_id   = v_data['contact']['facebook']
    except ParamError:
      return "Invalid id, check foursquare ID"

    new_doc = {
    '_id': venue,
    'name':  v_data['name'],
    'twitter': v_data['contact']['twitter'],
    'fb_id': v_data['contact']['facebook']
    }
    if untappd:
        try:
            if new_doc['untappd_id'] != untappd:
              new_doc['untappd_id'] = untappd
        except KeyError:
            new_doc['untappd_id'] = None

    doc = loc_db.get(id=venue)
    if doc == None:
        loc_db.save(doc)
    else:
        update = False
        for key in new_doc:
            if new_doc[key] != doc[key]:
                update = True

    if update:
        loc_db.save(doc)

    return simplejson.dumps(loc_db.get(venue))
