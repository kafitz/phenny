#!/usr/bin/env python
"""
weather.py - Phenny Weather Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Rewrite: Kyle Fitzsimmons 2013, http://kylefitz.com
"""

from urllib import quote
import urllib2
import simplejson as json
from geopy import geocoders

class CurrentConditions:
	"""Parser and container for JSON data
	"""
	def __init__(self, webpage_object):
		data = json.load(webpage_object)
		current_observation = data['current_observation']
		self.location = str(current_observation['display_location']['full'])
		self.weather = str(current_observation['weather'])
		self.temp_f = str(current_observation['temp_f'])
		self.temp_c = str(current_observation['temp_c'])
		self.rh = str(current_observation['relative_humidity'])
		self.pressure_mb = str(current_observation['pressure_mb'])
		self.wind_mph = str(current_observation['wind_mph'])
		self.wind_kph = str(current_observation['wind_kph'])
		self.wind_dir = str(current_observation['wind_dir'])
		self.wind_gust_mph = str(current_observation['wind_gust_mph'])
		self.wind_gust_kph = str(current_observation['wind_gust_kph'])
		self.precip_today_in = str(current_observation['precip_today_in'])
		self.precip_today_metric = str(current_observation['precip_today_metric'])
		self.time = str(current_observation['observation_time'])
		trend = str(current_observation['pressure_trend'])
		if trend == '+':
			self.pressure_trend = ' and rising'
		elif trend == '-':
			self.pressure_trend = ' and falling'
		elif trend == '0':
			self.pressure_trend = ' steady'
		else:
			self.pressure_trend = ' trend_error'

def get_weather(phenny, input):
	""".w zipcode - Fetches the weather report for the given zipcode (postal code; city, 
		state/country)
	"""
	def gcode(location):
		g = geocoders.Google()
		geocodes = g.geocode(input, exactly_one=False)
		place_string = geocodes[0][0] # Extract first result from list of tuple from 'non-exact' geocode
		latlng_tuple = geocodes[0][1]
		place_list = place_string.split(",")
		# For each region (city, state, country) in list, substitute a correctly encoded URL string
		# utf-8 must be specified since google can return unicode place names
		place_list = [quote(region_name.strip().encode('utf-8')) for region_name in place_list]
		debug_str = ", ".join(place_list)
		# Manually adjust for wunderground's inadequacies
		if len(place_list) > 2:
			# Wunderground fails if USA is on the end of US address or then otherwise if another
			# country's states/provinces are included in the search string
			if place_list[2] == "USA":
				place_list.pop()
			else:
				place_list.pop(1)
		place_url = ",".join(place_list)
		print latlng_tuple
		return place_url, latlng_tuple, debug_str

	def fetch_json(url):
		# open wunderground api url
		opener = urllib2.build_opener()
		req = urllib2.Request(url)
		json_object = opener.open(req)
		return json_object

	def output_results(phenny, webpage_object):
		reading = CurrentConditions(webpage_object)
		forecast_text = "Current weather for: " + "\x02" + reading.location + "\x02. " + \
						reading.weather + ", " + \
						reading.temp_f + "F/" + \
						reading.temp_c + "C. " + \
						"\x0302RH:\x0301 " + reading.rh + " " + \
						"\x0302Pressure (mB):\x0301 " + reading.pressure_mb + reading.pressure_trend + ". " + \
						"\x0302Wind:\x0301 " + reading.wind_mph + "mph/" + reading.wind_kph + "kph " + \
						"(gusts: " + reading.wind_gust_mph + "/" + reading.wind_gust_kph + ") " + \
						"from the " + reading.wind_dir + ". " + \
						"\x0302" + "Precipitation today: " + "\x0301" + \
						"\x0301" + reading.precip_today_in + "in/" + reading.precip_today_metric + "mm " + "\x0301" + \
						 "(" + reading.time + ")"
		phenny.say(forecast_text)
		return


	# create wunderground weather api url from google maps (since wundergrounds API geocode is rather poor)
	place_url, latlng_tuple, debug_str = gcode(input)
	base_url = "http://api.wunderground.com/api/%s/geolookup/conditions/q/" % input.weather_API
	json_file = place_url + ".json"
	search_url = base_url + json_file	
	try:
		json_object = fetch_json(search_url)
		output_results(phenny, json_object)
	except:
		# Say the closest found results to help user debug search input if possible
		try:
			search_url = base_url + str(latlng_tuple[0]) + "," + str(latlng_tuple[1]) + ".json"
			json_object = fetch_json(search_url)
			output_results(phenny, json_object)
		except:
			if "," in place_url:
				print "Search string: %s" % debug_str
				place_list = place_url.split(",")
				city_name = place_list[0]
				search_url = base_url + city_name + ".json"
				try:
					closest_matches = ""
					json_object = fetch_json(search_url)
					search_results = json.load(json_object)
					for result in search_results['response']['results']:
						say_str = str(result['city']) + ", " + str(result['state']) + ", " + str(result['country'])
						closest_matches = closest_matches + say_str + " / "
					closest_matches = closest_matches[:-2]
					phenny.say("Could not find results for %s. Found results instead for: " % debug_str + closest_matches)
				except: pass
			else:
				pass
get_weather.commands = ['w', 'weather']
get_weather.name = 'weather'
get_weather.example = '.w Montreal, Canada'


if __name__ == "__main__":
    print __doc__.strip()
