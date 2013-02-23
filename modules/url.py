#!/usr/bin/env python
"""
youtube_title.py - Phenny URL Title Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com
"""

import urllib2
import re
import HTMLParser

def url_announce(phenny, input):
	h = HTMLParser.HTMLParser()
	url_pattern = re.compile(r'http(s?)://\S+')
	title_regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
	# Try regex match for each word in line
	word_list = input.bytes.split(" ")
	for word_string in word_list:
		url_match = re.match(url_pattern, word_string)
		if url_match:
			url = url_match.group()
			# Follow page redirect if exists
			redirect_url = urllib2.urlopen(url).geturl()
			page_data = urllib2.urlopen(redirect_url).read()
			try:
				page_title_str = title_regex.search(page_data).group(1)
				page_title = page_title_str.strip()
				# Only output page titles longer than 3 words long to cut down on obvious page names like "Google" for google.com
				if len(page_title.split(" ")) > 3:
					irc_output = '\"' + page_title + '\"'
					phenny.say(h.unescape(irc_output))
			except:
				print "No <title> tag exists in linked URL's html."
	return
url_announce.rule = r'(.*?)https?://'
url_announce.name = 'url_announce'
url_announce.example = 'http://www.reuters.com --> irc_bot: "Breaking News, Top News & Latest News Headlines | Reuters.com"'
url_announce.priority = 'medium'


if __name__ == "__main__":
    print __doc__.strip()