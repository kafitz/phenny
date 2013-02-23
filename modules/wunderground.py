#!/usr/bin/env python
"""
wunderground.py - Phenny Weather Module for Interfacing with Wunderground API
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com/
"""

from urllib import quote
import urllib2
from geopy import geocoders
import simplejson as json

def gcode(phenny, location):
	g = geocoders.Google()
	geocodes = g.geocode(location.encode('utf-8'), exactly_one=False)
	place_string = geocodes[0][0] # Extract first result from list of tuple from 'non-exact' geocode
	latlng_tuple = geocodes[0][1]
	place_list = place_string.split(",")
	# For each region (city, state, country) in list, substitute a correctly encoded URL string
	# utf-8 must be specified since google can return unicode place names
	place_list = [quote(region_name.strip().encode('utf-8')) for region_name in place_list]
	# Manually adjust for wunderground's inadequacies
	if len(place_list) > 2:
		# Wunderground fails if USA is on the end of US address or then otherwise if another
		# country's states/provinces are included in the search string
		if place_list[2] == "USA":
			place_list.pop()
		else:
			place_list.pop(1)
	place_url = ",".join(place_list)
	return place_url, latlng_tuple

def fetch_json(url):
	# open wunderground api url
	opener = urllib2.build_opener()
	req = urllib2.Request(url)
	json_object = opener.open(req)
	return json_object

def format_json(phenny, location_str, api_key, report):
	# create wunderground weather api url from google maps (since wundergrounds API geocode is rather poor)
	place_url, latlng_tuple = gcode(phenny, location_str)

	base_url = "http://api.wunderground.com/api/%s/geolookup/%s/q/" % (api_key, report)
	json_file = place_url + ".json"
	search_url = base_url + json_file	
	json_object = fetch_json(search_url)
	json_data = json.load(json_object)
	if json_data['response'].get('error') or json_data['response'].get('results'): # Test to see if city not found or multiple results value in json response, attempt by lat/long
		search_url = base_url + str(latlng_tuple[0]) + "," + str(latlng_tuple[1]) + ".json"
		json_object = fetch_json(search_url)
		json_data = json.load(json_object)
		return json_data
	else:
		return json_data
