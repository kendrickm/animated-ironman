import couchdb
import config
import foursquare
import simplejson

#Takes a foursquare id and optional untappd venue id and uses that to build a
#location record our scrapers can use
def lookup_venue(venue, untappd=None):

    server = couchdb.client.Server(url=config.db_config['COUCHDB_SERVER'])
    loc_db = server['locations']
    try:
      client = foursquare.Foursquare(client_id=config.fsq_config['CLIENT_ID'],
      client_secret=config.fsq_config['CLIENT_SECRET'], version=config.fsq_config['API_VERSION'])
      v_data  = client.venues(venue)['venue']
    except ParamError:
      return "Invalid id, check foursquare ID"

    twitter = fb_id = ""
    contact_info = v_data['contact']
    if 'twitter' in contact_info.keys():
        twitter =  contact_info['twitter']
    if 'facebook' in contact_info.keys():
        fb_id   = contact_info['facebook']

    new_doc = {
    '_id': venue,
    'name':  v_data['name'],
    'twitter': twitter,
    'fb_id': fb_id,
    }

    if untappd: #We passed in an untappd id
        try:
            if new_doc['untappd_id'] != untappd: #Check to see if its different then existing
              new_doc['untappd_id'] = untappd
        except KeyError:
            new_doc['untappd_id'] = untappd

    doc = loc_db.get(id=venue) #Try and pull existing doc from db if it exists
    update = False
    if doc == None: #Doc doesn't exist
        update = True
    else:
        for key in new_doc: #Check each key for something different, if so then we'll update the db
            try:
                if new_doc[key] != doc[key]:
                    update = True
            except KeyError:
                update = True
    if update:
        loc_db.save(new_doc)

    return simplejson.dumps(loc_db.get(venue)) #Return a json value of our db record


#
# def lookup_untappd():
#
# def lookup_twitter():
#
# def lookup_facebook():
