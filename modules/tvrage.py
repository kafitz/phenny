#!/usr/bin/python
"""
tvrage.py - Phenny TVRage.com Module
Kyle Fitzsimmons 2013, http://kylefitz.com
"""

from urllib import quote
import urllib2

# Set tag colors (mirc colors with \x tag - e.g., \x01[,00] for black text on white bg)
SCRIPT_HEADER = "\x0302TV: \x0301"
TAG_FORMAT = "\x0302" # color of the "category_name: " tag - e.g., "Show name: "
DATA_FORMAT = "\x02\x0301" # bold + color of the tv informator
BULLET = u"\u2022" # bullet point text divider

class TVData:
	def __init__(self):
		pass

def tvrage(phenny, input):
	""".tv tv_show - Fetches info on next and last broadcasts from TVRage.com
	"""
	unicode_input = unicode(input)
	search_str = unicode_input.encode('utf-8')
	phenny.say("Searching...")
	tv_data = TVData()

	# --TVRage API parsing--
	# Create the search for the input tv show
	formatted_query = quote(search_str)
	search_url = "http://services.tvrage.com/tools/quickinfo.php?show=%s" % formatted_query
	opener = urllib2.build_opener()
	request = urllib2.Request(search_url)
	setattr(tv_data, 'raw_output', opener.open(request))
	for line in tv_data.raw_output:
		cleaned_line = line.strip()
		line_list = cleaned_line.split('@') # '@' is the divisor for tvrage data tags and values
		line_list[0] = "".join(line_list[0].split(" "))
		if line_list[0].isalpha() is True:
			try:
				line_list.append(line_list[1].split("^"))
				line_list.pop(1)
			except: pass
			setattr(tv_data, line_list[0], line_list[1])
		else:
			pass # Ignore setting attributes with non-alphabetic characters in the tag's name

	def df(attribute_name):
		return DATA_FORMAT + attribute_name + DATA_FORMAT

	# --Phenny IRC output--
	tf = TAG_FORMAT
	try:
		one = tf + "Show: " + df(tv_data.ShowName[0]) + DATA_FORMAT + " (" + tv_data.Premiered[0] + ") " + DATA_FORMAT + BULLET + tf + " Status: " + df(tv_data.Status[0]) + " " + BULLET + " "
		two = tf + "Previous Ep: " + df(tv_data.LatestEpisode[0]) + " on " + df(tv_data.LatestEpisode[2]) + " " + BULLET + tf + " Next Ep: "
		three = df(tv_data.NextEpisode[0]) + " on " + df(tv_data.NextEpisode[2]) + " at " + df(tv_data.Airtime[0][-8:])
		phenny_output = one + two + three
		phenny.say(phenny_output)
	except AttributeError:
		phenny.say("Couldn't find show TVRage, please try again.")
	except:
		phenny.say("Critical generic unspecified error.")
tvrage.commands = ['tv']
tvrage.name = 'tv'
tvrage.example = '.tv The Wire'

	
if __name__ == '__main__':
	main()