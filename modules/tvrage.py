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
		self.Airtime = None
		self.Classification = None
		self.Country = None
		self.Ended = None
		self.Genres = None
		self.LatestEpisode = None
		self.Network = None
		self.NextEpisode = None
		self.Premiered = None
		self.Runtime = None
		self.ShowName = None
		self.ShowURL = None
		self.Started = None
		self.Status = None

def tvrage(phenny, input):
	""".tv tv_show - Fetches info on next and last broadcasts from TVRage.com
	"""
	unicode_input = unicode(input[4:]) # strip '.tv' command data prefix
	search_str = unicode_input.encode('utf-8')
	phenny.say("Searching...")
	tv_data = TVData()

	# --TVRage API parsing--
	# Create the search for the input tv show
	formatted_query = quote(search_str)
	search_url = "http://services.tvrage.com/tools/quickinfo.php?show=%s" % formatted_query
	print search_url
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

	def df(attribute_data):
		return DATA_FORMAT + attribute_data + DATA_FORMAT

	# --Phenny IRC output--
	try:
		show_name = tv_data.ShowName[0]
	except AttributeError:
		phenny.say("Couldn't find show on TVRage, please try again.")
	premiered = df(tv_data.Premiered[0]) if tv_data.Premiered else ""
	status = df(tv_data.Status[0]) if tv_data.Status else ""
	latest_ep_id = df(tv_data.LatestEpisode[0]) if tv_data.LatestEpisode else ""
	latest_ep_date = df(tv_data.LatestEpisode[2]) if tv_data.LatestEpisode else ""
	next_ep_id = df(tv_data.NextEpisode[0]) if tv_data.NextEpisode else ""
	next_ep_date = df(tv_data.NextEpisode[2]) if tv_data.NextEpisode else ""
	ended_date = df(tv_data.Ended[0]) if tv_data.Ended else ""
	airtime = df(tv_data.Airtime[0][-8:]) if tv_data.Airtime else ""

	tf = TAG_FORMAT
	if show_name:
		one = tf + "Show: " + df(show_name) + DATA_FORMAT + " (" + premiered + ") " + DATA_FORMAT + BULLET + tf + " Status: " + status
		two = " " + BULLET + " " + tf + "Previous Ep: " + latest_ep_id + " on " + latest_ep_date + " "
		if not next_ep_id == "":
			next_ep = BULLET + tf + " Next Ep: " + next_ep_id + " on " + next_ep_date + " at " + airtime
			phenny_output = one + two + next_ep
		elif not ended_date == "":
			ended = BULLET + tf + " Ended on: " + ended_date
			phenny_output = one + ended
		else:
			phenny_output = one + two
		phenny.say(phenny_output)
	else:
		pass # No show found to concatenate string from
tvrage.commands = ['tv']
tvrage.name = 'tv'
tvrage.example = '.tv The Wire'

	
if __name__ == '__main__':
	main()