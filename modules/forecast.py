#!/usr/bin/env python
"""
forecast.py - Phenny Weather Forecast Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com/
"""

import wunderground as wg

class Forecast:
	def __init__(self, webpage_object):
		data = json.load(webpage_object)

def get_forecast(phenny, input):
	""".fc zipcode - Fetches the daily forecast for the given zipcode (postal code; city, 
		state/country)"""

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

	location_str = unicode(input)

	try:
		json_object = wg.format_json(location_str)
		output_results(phenny, json_object)
	except geocoders.google.GQueryError:
		phenny.say('Could not find results for "%s", please reword the search and try again.' % location_str[3:])
get_weather.commands = ['fc', 'forecast']
get_weather.name = 'forecast'
get_weather.example = '.fc Montreal, Canada'


if __name__ == "__main__":
    print __doc__.strip()
