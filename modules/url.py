#!/usr/bin/env python
"""
youtube_title.py - Phenny URL Title Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, http://kylefitz.com
-Announce URLs for page titles longer than 3 words and post them to a twitter feed
"""

import urllib2
import re
import HTMLParser
import twitter

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
			pic_exts = ['.jpg', '.png', '.gif', 'jpeg']
			try:
				page_title_str = title_regex.search(page_data).group(1)
				page_title = page_title_str.strip()
				# Only output page titles longer than 3 words long to cut down on obvious page names like "Google" for google.com
				if len(page_title.split(" ")) > 3:
					# Add quotes to output string and convert HTML character codes to unicode w/ HTMLParser
					irc_output = h.unescape('\"' + page_title + '\"')
					phenny.say(irc_output)
					page_title_len = 4
				else:
					page_title_len = 0
			except Exception, e:
				print "No <title> tag exists in linked URL's html."
				page_title_len = 0
			# Escape own twitter handle link
			if "RobotoRoberto" in url:
				pass
			elif page_title_len > 3 or url[-4:] in pic_exts:
				twitter_api = twitter.Api(input.twitter_consumer_key,
											input.twitter_consumer_secret,
											input.twitter_access_token_key,
											input.twitter_access_token_secret)
				if page_title_len == 0:
					twitter_update = str(redirect_url)
				else:
					twitter_update = str(redirect_url) + " - " + str(page_title)
				try:
					twitter_api.PostUpdate(twitter_update)
				except twitter.TwitterError, e:
					print e
	return
url_announce.rule = r'(.*?)https?://'
url_announce.name = 'url_announce'
url_announce.example = 'http://www.reuters.com --> irc_bot: "Breaking News, Top News & Latest News Headlines | Reuters.com"'
url_announce.priority = 'medium'


if __name__ == "__main__":
    print __doc__.strip()