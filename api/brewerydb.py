import requests
import config
import json
import urllib
import re
from normutil import similar

auth_info = "key=%s" % (config.bdb_config["API_KEY"]) #Add the api key to all requests

#Base function to make all REST requests
def requester(path, query_params = ""):
    url = config.bdb_config['BASE_URL'] + "/%s/?%s&%s" % (path, query_params, auth_info)
    #print "Requesting %s" % (url)
    r = requests.get(url)
    response = json.loads(r.text)
    if response['status'] == "success":
        return response
    else:
        return None

#Iterates through through building the passed search text from 1 word to full list
#Returns a hash of any results that return from the searches
def brewery_search_name(text):
    print "Doing a full search on %s" %(text)
    words = text.split()
    check_string = ""
    brewery_hash = {}

    for w in words:
        check_string = check_string + " " + w
        encoded_string = urllib.quote_plus(check_string) #Encodes string to be passed in url
        print "Checking %s encoded string is %s" %(check_string, encoded_string)
        try:
            parsed_data = requester("breweries", "name=%s*" % (encoded_string))
            if (parsed_data['totalResults'] > 0):
                brewery_hash[check_string] = parsed_data
        except KeyError: #Catching this exception because results of 0 don't have that key
            print "No results for " + check_string

    brewery_data = None
    lowest_count = None
    for brewery_list in brewery_hash.values():
        if brewery_list['totalResults'] == 1: #If theres only one result, this is what we want
            print "Found 1 result, using that"
            lowest_count = 1
            return brewery_list
        elif lowest_count == None: #If lowest_count isn't set, this is probably the first in the loop
            #print "Lowest count isn't set, using this as baseline"
            lowest_count = brewery_list['totalResults']
            brewery_data = brewery_list
        elif lowest_count > brewery_list['totalResults']: #If this is a smaller subset of breweries, use this
            #print "This is the new lowest count, should use this now"
            lowest_count = brewery_list['totalResults']
            brewery_data = brewery_list

    if brewery_data is None:
        print "We were unable to find a brewery"
        return None
    print "We have %s breweries to review" % (lowest_count)
    return brewery_data


#Searches passed in brewery id for the search text
def beer_search_by_brewery(brewery_id, brewery_name, full_search_text):
    yank_words = ""
    # print "Checking %s in %s" % (brewery_name, full_search_text)
    split_name = brewery_name.split(" ")
    split_words = full_search_text.split(" ")
    legit_words = []

    try:
        results_list = {}
        beer_list = requester("brewery/%s/beers" %(brewery_id))['data']
        for word in split_words:
            print "Now searching %s" % (word)
            if word in split_name:
                print "%s looks to be part of the brewery name %s, skipping..." % (word, brewery_name)
            else:
                legit_words.append(word)
                regex = re.compile(".*%s.*" % (word)) #Sometimes beers have IPA etc. after them in the official name
                for beer in beer_list:
                    print "Is %s what we want?" % (beer['name'])
                    if re.match(regex, beer['name']):
                        print "YESSSSSS"
                        results_list[beer['id']] = beer['name']
    except KeyError:
        print "No data found, beer must not exist"
    if len(results_list) == 0:
        print "Looks like nothing found"
        return None
    elif len(results_list) == 1:
        return results_list.iterkeys().next()
    else:
        print "Found multiple options, gonna give it one more shot!"
        return hopefully_find(legit_words, results_list)

def beer_lookup(beer_id):
    response = requester("beer/%s" % (beer_id))
    return response['data']

def brewery_lookup_by_beer(beer_id):
    response = requester("beer/%s/breweries" % (beer_id))
    return response['data'][0]


#Takes a passed in string and searches for breweries/beers that could be found in the string
def brewerydb_full_search(text):
    breweries = brewery_search_name(text)
    if breweries is None:
        return None
    if breweries['totalResults'] == 1: #Only one brewery returned
        brewery_data = breweries['data'][0]
        print "We are going with %s with id of %s" % (brewery_data['name'], brewery_data['id'])
        regex = re.compile("^%s" % (brewery_data['name']))
        search_text = regex.sub("", text)
        return beer_search_by_brewery(brewery_data['id'], brewery_data['name'], search_text)
    else:
        brewery_data = breweries['data']
        count = len(brewery_data)
        print "We have a list of %s breweries to search" % (count)
        for brewery in brewery_data:
            print "Searching %s" % (brewery['name'])
            regex = re.compile("^%s" % (brewery['name']))
            search_text = regex.sub("", text)
            beer = beer_search_by_brewery(brewery['id'], brewery['name'], search_text)
            if beer != None:
                return beer

def hopefully_find(word_list, beer_dict):
    search_phrase = " ".join(word_list)
    print search_phrase
    for beer_id, name in beer_dict.iteritems():
        search_percentage = similar(search_phrase, name)
        if  search_percentage > .75:
            print "%s is a good bet at %% %s" % (name, search_percentage)
            return beer_id
    print "Didn't get anywhere"
    return False
