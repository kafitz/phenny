#!/usr/bin/env python
"""
forecast.py - Phenny Weather Forecast Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com/
"""

class Forecast:
	def __init__(self, json_data):
		city = str(json_data['location']['city'])
		try: state = str(json_data['location']['state'])
		except: pass
		country_name = str(json_data['location']['country_name'])
		self.forecast = json_data['forecast']['simpleforecast']['forecastday']
		self.period1_date = str(self.forecast[0]['date']['pretty'])
		self.period1_conditions = str(self.forecast[0]['conditions'])
		self.period1_highf = str(self.forecast[0]['high']['fahrenheit'])
		self.period1_highc = str(self.forecast[0]['high']['celsius'])
		self.period1_lowf = str(self.forecast[0]['low']['fahrenheit'])
		self.period1_lowc = str(self.forecast[0]['low']['celsius'])
		self.period1_PoP = str(self.forecast[0]['pop'])
		self.period1_meltin = str(self.forecast[0]['qpf_allday']['in'])
		self.period1_meltmm = str(self.forecast[0]['qpf_allday']['mm'])
		self.period1_snowin = str(self.forecast[0]['snow_allday']['in'])
		self.period1_snowcm = str(self.forecast[0]['snow_allday']['cm'])
		self.period1_avgwindmi = str(self.forecast[0]['avewind']['mph'])
		self.period1_avgwindkm = str(self.forecast[0]['avewind']['kph'])
		self.period1_winddir = str(self.forecast[0]['avewind']['dir'])
		self.period2_date = str(self.forecast[1]['date']['pretty'])
		self.period2_conditions = str(self.forecast[1]['conditions'])
		self.period2_highf = str(self.forecast[1]['high']['fahrenheit'])
		self.period2_highc = str(self.forecast[1]['high']['celsius'])
		self.period2_lowf = str(self.forecast[1]['low']['fahrenheit'])
		self.period2_lowc = str(self.forecast[1]['low']['celsius'])
		self.period2_PoP = str(self.forecast[1]['pop'])
		self.period2_meltin = str(self.forecast[1]['qpf_allday']['in'])
		self.period2_meltmm = str(self.forecast[1]['qpf_allday']['mm'])
		self.period2_snowin = str(self.forecast[1]['snow_allday']['in'])
		self.period2_snowcm = str(self.forecast[1]['snow_allday']['cm'])
		self.period2_avgwindmi = str(self.forecast[1]['avewind']['mph'])
		self.period2_avgwindkm = str(self.forecast[1]['avewind']['kph'])
		self.period2_winddir = str(self.forecast[1]['avewind']['dir'])

		if state:
			self.location = city + ", " + state
		else:
			self.location = city + ", " + country_name

		
def output_results(phenny, json_data):
	reading = Forecast(json_data)
	forecast1_text_pt1 = "Forecast for " + "\x02" + reading.location + "\x02 at " + \
						reading.period1_date + ". " + reading.period1_conditions + ". " + \
						"Highs of " + reading.period1_highf + "F/" + \
						reading.period1_highc + "C, lows of " + \
						reading.period1_lowf + "F/" + reading.period1_lowc + "C. " + \
						"\x0302PoP:\x0301 " + reading.period1_PoP + "% " + \
						"\x0302Precip. (melt):\x0301 " + reading.period1_meltin + "in/" + reading.period1_meltmm+ "mm. "
	forecast1_text_pt2 = "\x0302Wind:\x0301 " + reading.period1_avgwindmi + "mph/" + reading.period1_avgwindkm + "kph " + \
						"from the " + reading.period1_winddir + ". "
	if str(reading.period1_snowcm) is not '0':
		forecast1_text = forecast1_text_pt1 + "\x0302Snow:\x03 " + reading.period1_snowin + "in/" + reading.period1_snowcm + "cm. " + forecast1_text_pt2
	else:
		forecast1_text = forecast1_text_pt1 + forecast1_text_pt2

	forecast2_text_pt1 = "Forecast -- " + reading.period2_date + ": " + reading.period2_conditions + ". " + \
						"Highs of " + reading.period2_highf + "F/" + \
						reading.period2_highc + "C, lows of " + \
						reading.period2_lowf + "F/" + reading.period2_lowc + "C. " + \
						"\x0302PoP:\x0301 " + reading.period2_PoP + "% " + \
						"\x0302Precip. (melt):\x0301 " + reading.period2_meltin + "in/" + reading.period2_meltmm+ "mm. "

	forecast2_text_pt2 = "\x0302Wind:\x0301 " + reading.period2_avgwindmi + "mph/" + reading.period2_avgwindkm + "kph " + \
						"from the " + reading.period2_winddir + ". "
	if str(reading.period2_snowcm) is not '0':
		forecast2_text = forecast2_text_pt1 + "\x0302Snow:\x03 " + reading.period2_snowin + "in/" + reading.period2_snowcm + "cm. " + forecast2_text_pt2
	else:
		forecast2_text = forecast2_text_pt1 + forecast2_text_pt2

	phenny.say(forecast1_text)
	phenny.say(forecast2_text) # Two forecasts 24-hr apart
	return

def get_forecast(phenny, input):
	""".fc zipcode - Fetches the daily forecast for the given zipcode (postal code; city, 
		state/country)"""
	import wunderground

	report_type = 'forecast'

	unicode_input = unicode(input)
	if unicode_input[1:9] == 'forecast':
		location_str = unicode_input[10:]
	elif unicode_input[1:4] == 'fc ':
		location_str = unicode_input[4:]

	# try:
	json_data = wunderground.format_json(phenny, location_str, input.weather_API, report_type)
	output_results(phenny, json_data)
	# except Exception, e:
	# 	print e
	# 	phenny.say('Could not find results for "%s", please reword the search and try again.' % location_str)
get_forecast.commands = ['fc', 'forecast']
get_forecast.name = 'forecast'
get_forecast.example = '.fc Montreal, Canada'


if __name__ == "__main__":
    print __doc__.strip()
