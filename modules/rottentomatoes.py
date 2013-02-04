#!/usr/bin/env python
"""
rottentomatoes.py - Phenny RottenTomatoes.com Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com
"""

from urllib import urlencode
from urllib2 import urlopen
import simplejson as json

# Set tag colors (mirc colors with \x tag - e.g., \x01[,00] for black text on white bg)
SCRIPT_HEADER = "\x0304Rotten\x0303Tomatoes\x0301 - "
TAG_FORMAT = "\x0302" # color of the "category_name: " tag - e.g., "Movie name: "
DATA_FORMAT = "\x02\x0301" # bold + color of the displayed data following tag - e.g., "Finding Nemo"

class JSONparser:
	"""Creates an individual attribute (in self) for each data pair in the JSON file and tries to name
	nested layers logically (i.e., self.categoryName_subcat1_subcat2 ... etc)
	"""
	def __init__(self, JSON_movie_info):
		for data_category in JSON_movie_info:
			category_values = JSON_movie_info[data_category]
			if isinstance(category_values, int):
				category_values = str(category_values)
			# If string, immediately set value to an attribute of JSONparser
			elif isinstance(category_values, basestring):
				colored_output = DATA_FORMAT + category_values + DATA_FORMAT # appended at end as well to clear formatting
				setattr(JSONparser, data_category, colored_output)
			# If dict, loop through each key:pair and create a unique attribute for each with the dict's name as prefix
			elif isinstance(category_values, dict):
				for attribute_name in category_values:
					subcategory_name = str(data_category) + "_" + str(attribute_name)
					colored_output = DATA_FORMAT + str(category_values[attribute_name]) + DATA_FORMAT
					setattr(JSONparser, subcategory_name, colored_output)
			# Anything else, pass as is to handle case-by-case
			else:
				setattr(JSONparser, data_category, category_values)


# Based off https://github.com/zachwill/rottentomatoes/blob/master/rottentomatoes/rottentomatoes.py
def rottentomatoes(phenny, input, **kwargs):
	""".rt movie_name - Fetches info from rottentomatoes API about the given movie
	"""
	base_url = 'http://api.rottentomatoes.com/api/public/v%s/' % input.rottentomatoes_API_version
	movie_url = base_url + 'movies'
	
	# Find the movie on rt: create a list of the url search string elements
	search_url = [movie_url, '?']
	movie_name = input[4:]
	kwargs.update({'apikey': input.rottentomatoes_API, 'q': movie_name})
	search_url.append(urlencode(kwargs)) # Create the URL
	rt_search_json = json.loads(urlopen(''.join(search_url)).read())
	if not rt_search_json['movies']:
		phenny.say('Film "%s" not found, please try again.' % input[4:])
	else:
		# From the first result of the 'movies' list, return the link to individual movie's JSON file
		self_json_url = rt_search_json['movies'][0]['links']['self']

		# Get the individual movie's JSON file and parse it to a class object
		self_url = self_json_url + "?" + urlencode({'apikey': input.rottentomatoes_API})
		JSON_movie_info = json.loads(urlopen(self_url).read())
		movie_data = JSONparser(JSON_movie_info)
		print dir(movie_data)

		# For some reason, runtime seems to only be returned from the original search results JSON
		# so it gets explicitly set here
		runtime = self_json_url = rt_search_json['movies'][0]['runtime']
		movie_data.runtime = DATA_FORMAT + str(runtime) + DATA_FORMAT

		def list_to_str(list_name):
			return_str = str(DATA_FORMAT)
			list_string = ", ".join(list_name)
			return_str = return_str + list_string + DATA_FORMAT
			return return_str

		def dict_entry(dict_name):
			# For extracting the string of a single entry dict or list of a dict
			# (i.e., director_name = [{'name': 'Tom Shadyac'}])
			try:
				# If list select the first entry, otherwise do nothing
				true_dict = dict_name[0]
			except:
				true_dict = dict_name
			for key in true_dict:
				dict_element = DATA_FORMAT + str(true_dict[key]) + DATA_FORMAT
			return dict_element

		# Strip premature mirc color tag on IMDb string (displayed as hotlink so unneeded anyway)
		imdb_id = movie_data.alternate_ids_imdb[4:-3]
		imdb_url = "http://www.imdb.com/title/tt" + imdb_id

		# # Format the IRC response
		tf = TAG_FORMAT
		one = SCRIPT_HEADER + tf + "Title: " + movie_data.title + tf + " Runtime: " + movie_data.runtime
		two = tf + " Release date: " + movie_data.release_dates_theater
		three = tf + " MPAA rating: " + movie_data.mpaa_rating + tf + " Director: " + dict_entry(movie_data.abridged_directors)
		four = tf + " Critic score: " + movie_data.ratings_critics_score + tf + " Audience score: " + movie_data.ratings_audience_score 
		five = tf + " Link: " + movie_data.links_alternate + tf + " IMDb: " + imdb_url

		phenny_output = one + two + three + four + five
		phenny.say(phenny_output)
rottentomatoes.commands = ['rt']
rottentomatoes.name = 'rt'
rottentomatoes.example = '.rt Finding Nemo'

if __name__ == "__main__":
    print __doc__.strip()