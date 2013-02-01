#!/usr/bin/env python
"""
rottentomatoes.py - Phenny RottenTomatoes.com Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, kylefitz.com
"""

from urllib import urlencode
from urllib2 import urlopen
import simplejson as json

# Based off:
# https://github.com/zachwill/rottentomatoes/blob/master/rottentomatoes/rottentomatoes.py
def rottentomatoes(phenny, input, **kwargs):
	""" .rt movie_name - Fetches info from rottentomatoes API about the given movie
	"""
	base_url = 'http://api.rottentomatoes.com/api/public/v%s/' % input.rottentomatoes_API_version
	lists_url = base_url + 'lists'
	movie_url = base_url + 'movies'
	search_url = [movie_url, '?']
	movie_name = input[4:]
	kwargs.update({'apikey': input.rottentomatoes_API, 'q': movie_name})
	search_url.append(urlencode(kwargs))
	data = json.loads(urlopen(''.join(search_url)).read())
	print data['total']

rottentomatoes.commands = ['rt']
rottentomatoes.name = 'rt'
rottentomatoes.example = '.rt Finding Nemo'

if __name__ == "__main__":
    print __doc__.strip()