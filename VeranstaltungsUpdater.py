import datetime, hashlib, hmac, json, os, pytz, random, string, sys, time, requests
#from fabric.api import *
#from fabric.operations import local
from string import Template

events_url = 'http://jetzt.aufstehen.de/page/event/search_results?country=DE&limit=5000&format=json'

resp = requests.get(events_url)
print "Request complete."

data = json.loads(resp.text)
print "JSON loaded."

global rsvp_count
rsvp_count = 0

def clean_result(row):
        global rsvp_count
        for key in ['description', 'closed_msg', 'distance']:
            if key in row:
                del row[key]

        location_fields = filter(lambda x: x in row, ['venue_name', 'venue_addr1', 'venue_city', 'venue_state_cd', 'venue_zip'])
        row['location'] = " ".join(row[key] for key in location_fields)

        for key in ['venue_name', 'venue_addr1', 'venue_city', 'venue_state_cd']:
            if key in row:
                del row[key]

        # not sure we need these?
        for key in ['type_id', 'timezone']:
            if key in row:
                del row[key]

        # rsvp_count += row['depl_count']
        rsvp_count += row['attendee_count'] if 'attendee_count' in row else 0
        return row

data_out = {'results': map(clean_result, data['results'])}


data['settings']['rsvp'] = rsvp_count
data['settings']['count'] = 3520 # hax.

print "JSON cleaned! %s events, %s RSVP's." % (len(data['results']), data['settings']['rsvp'])

data_out['settings'] = data['settings']

json_dump = json.dumps(data_out)
eventsjson = json.dumps(data_out)

jsonfile = open('d/events.json', 'w')
jsonfile.write(eventsjson)
jsonfile.close()

json_dump = "window.EVENT_DATA = " + json_dump

print "Writing data..."

outfile = open('js/event-data.js', 'w')
outfile.write(json_dump)
outfile.close()

print "Done! GZipping..."

