#!/usr/bin/env python
"""
weather.py - Phenny Weather Current Conditions Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com/
"""

import simplejson as json

class CurrentConditions:
	"""Parser and container for JSON data"""
	def __init__(self, json_data):
		current_observation = json_data['current_observation']
		self.location = str(current_observation['display_location']['full'])
		self.weather = str(current_observation['weather'])
		self.temp_f = str(current_observation['temp_f'])
		self.temp_c = str(current_observation['temp_c'])
		self.feelslike_f = str(current_observation['feelslike_f'])
		self.feelslike_c = str(current_observation['feelslike_c'])
		self.rh = str(current_observation['relative_humidity'])
		self.pressure_mb = str(current_observation['pressure_mb'])
		self.wind_string = str(current_observation['wind_string'])
		self.wind_mph = str(current_observation['wind_mph'])
		self.wind_kph = str(current_observation['wind_kph'])
		self.wind_dir = str(current_observation['wind_dir'])
		self.wind_gust_mph = str(current_observation['wind_gust_mph'])
		self.wind_gust_kph = str(current_observation['wind_gust_kph'])
		self.precip_today_in = str(current_observation['precip_today_in'])
		self.precip_today_metric = str(current_observation['precip_today_metric'])
		self.time = str(current_observation['observation_time'])[16:] # Strip the "Last Updated on" portion
		trend = str(current_observation['pressure_trend'])
		if trend == '+':
			self.pressure_trend = ' and rising'
		elif trend == '-':
			self.pressure_trend = ' and falling'
		elif trend == '0':
			self.pressure_trend = ' steady'
		else:
			self.pressure_trend = ' trend_error'

def output_results(phenny, webpage_object):
	reading = CurrentConditions(webpage_object)
	conditions_text = "Current weather for " + "\x02" + reading.location + "\x02. " + \
					reading.weather + ", " + \
					reading.temp_f + "F/" + \
					reading.temp_c + "C " + \
					"(feels like " + reading.feelslike_f + "F/" + reading.feelslike_c + "C). " + \
					"\x0302RH:\x0301 " + reading.rh + " " + \
					"\x0302Pressure (mB):\x0301 " + reading.pressure_mb + reading.pressure_trend + ". " + \
					"\x0302Wind:\x0301 " + reading.wind_mph + "mph/" + reading.wind_kph + "kph " + \
					"(gusts: " + reading.wind_gust_mph + "/" + reading.wind_gust_kph + ") " + \
					"from the " + reading.wind_dir + ". " + \
					 "(updated " + reading.time + ")"
	phenny.say(conditions_text)
	return

def get_weather(phenny, input):
	""".w zipcode - Fetches the weather report for the given zipcode (postal code; city, 
		state/country)
	"""
	import wunderground

	api_key = input.weather_API

	unicode_input = unicode(input)
	if unicode_input[1:8] == 'weather':
		location_str = unicode_input[9:]
	elif unicode_input[1:3] == 'w ':
		location_str = unicode_input[3:]
	try:
		json_data = wunderground.format_json(phenny, location_str, api_key)
		output_results(phenny, json_data)
	# except geocoders.google.GQueryError:
	except:
		phenny.say('Could not find results for "%s", please reword the search and try again.' % location_str)
get_weather.commands = ['w', 'weather']
get_weather.name = 'weather'
get_weather.example = '.w Montreal, Canada'


if __name__ == "__main__":
    print __doc__.strip()
