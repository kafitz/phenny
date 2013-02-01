#!/usr/bin/env python
"""
weather.py - Phenny Weather Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Rewrite: Kyle Fitzsimmons 2013, kylefitz.com
"""

import urllib2
import simplejson as json

class CurrentConditions(object):
	''' Parser and container for JSON data '''
	def __init__(self, webpage_object):
		data = json.load(webpage_object)
		current_observation = data['current_observation']
		self.location = str(current_observation['display_location']['full'])
		self.weather = str(current_observation['weather'])
		self.temp_f = str(current_observation['temp_f'])
		self.temp_c = str(current_observation['temp_c'])
		self.rh = str(current_observation['relative_humidity'])
		self.pressure_mb = str(current_observation['pressure_mb'])

		trend = str(current_observation['pressure_trend'])
		print trend
		if trend == '+':
			self.pressure_trend = ' and rising'
		elif trend == '-':
			self.pressure_trend = ' and falling'
		elif trend == '0':
			self.pressure_trend = ' steady'
		else:
			self.pressure_trend = ' trend_error'

		self.wind_mph = str(current_observation['wind_mph'])
		self.wind_kph = str(current_observation['wind_kph'])
		self.wind_dir = str(current_observation['wind_dir'])
		self.wind_gust_mph = str(current_observation['wind_gust_mph'])
		self.wind_gust_kph = str(current_observation['wind_gust_kph'])
		self.precip_today_in = str(current_observation['precip_today_in'])
		self.precip_today_metric = str(current_observation['precip_today_metric'])
		self.time = str(current_observation['observation_time'])


def get_weather(phenny, input):
	""".w zipcode - Fetches the weather report for the given zipcode (postal code; city, 
		state/country)"""
	# remove all whitespace from geographic identifier (zip, postal code, city)
	geolookup = ''.join(input.group(2).split())
	# create google weather api url
	url = "http://api.wunderground.com/api/" + input.weather_API + \
			"/geolookup/conditions/q/" + geolookup + ".json"

	try:
		# open wunderground api url
		req = urllib2.Request(url)
		opener = urllib2.build_opener()
		webpage_object = opener.open(req)
	except:
		# if there was an error opening the url, return
		phenny.say("Error opening url")

	# parse json contents
	try:
		reading = CurrentConditions(webpage_object)
		forecast_text = "Current weather for: " + "\x02" + reading.location + "\x02. " + \
						reading.weather + ", " + \
						reading.temp_f + "F/" + \
						reading.temp_c + "C. " + \
						"\x0314RH:\x0301 " + reading.rh + " " + \
						"\x0314Pressure (mB):\x0301 " + reading.pressure_mb + reading.pressure_trend + ". " + \
						"\x0314Wind:\x0301 " + reading.wind_mph + "mph/" + reading.wind_kph + "kph " + \
						"(gusts: " + reading.wind_gust_mph + "/" + reading.wind_gust_kph + ") " + \
						"from the " + reading.wind_dir + ". " + \
						"\x0314" + "Precipitation today: " + "\x0301" + \
						"\x0302" + reading.precip_today_in + "in/" + reading.precip_today_metric + "mm " + "\x0301" + \
						 "(" + reading.time + ")"
		phenny.say(forecast_text)
	except:
		phenny.say("Non-specific JSON received, please retry the search.")


get_weather.commands = ['w', 'weather']
get_weather.name = 'weather'
get_weather.example = '.w Montreal, Canada'


if __name__ == "__main__":
    print __doc__.strip()
