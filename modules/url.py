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

def url_announce(phenny, input):
	url_pattern = re.compile(r'http(s?)://\S+')
	word_list = input.bytes.split(" ")
	url_list = []
	for word_string in word_list:
		url_match = re.match(url_pattern, word_string)
		if url_match:
			url = url_match.group()
			url_list.append(url)
	title_regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
	for url in url_list:
		redirect_url = urllib2.urlopen(url).geturl()
		page_data = urllib2.urlopen(redirect_url).read()
		page_title = title_regex.search(page_data).group(1)
		irc_output = '"' + page_title + '"'
		phenny.say(irc_output)
	return
url_announce.rule = r'(.*?)https?://'
url_announce.name = 'url_announce'
url_announce.example = 'http://www.reuters.com --> irc_bot: "Breaking News, Top News & Latest News Headlines | Reuters.com"'
url_announce.priority = 'medium'


if __name__ == "__main__":
    print __doc__.strip()