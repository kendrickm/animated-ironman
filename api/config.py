import yaml
config     = yaml.load(file('config/config.yml', 'r'))
db_config  = config['db']
fsq_config = config['foursquare']
bdb_config = config['brewerydb']
