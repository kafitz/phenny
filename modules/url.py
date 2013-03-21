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
from BeautifulSoup import BeautifulStoneSoup

def url_announce(phenny, input):
    '''Watches irc channels for urls in what users say, gets their pagle title, and
        posts to a twitter account (if set up). '''
    h = HTMLParser.HTMLParser()
    url_pattern = re.compile(r'http(s?)://\S+')
    title_regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
    # Try regex match for each word in line
    word_list = input.bytes.split(" ")
    for word_string in word_list:
        url_match = re.match(url_pattern, word_string)
        pic_exts = ['.jpg', '.png', '.gif', 'jpeg'] # Picture extensions to override minimum word count for twitter update
        if url_match:
            url = url_match.group()
            try: ## Follow page redirect if exists
                redirect_url = urllib2.urlopen(url).geturl()
                page_data = urllib2.urlopen(redirect_url).read()
                url = redirect_url
            except Exception, e:
                print e
            try: ## Fetch page url and say it to IRC channel
                title_html_str = title_regex.search(page_data).group(1)
                title_html = title_html_str.strip()
                # Convert HTML entities to unicode entities (for accented and special characters that lxml and HTML parser don't deal with)
                title_list = BeautifulStoneSoup(title_html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents
                page_title = title_list[0]
                # Only output page titles longer than 3 words long to cut down on obvious page names like "Google" for google.com
                if len(page_title.split(" ")) > 3:
                    # Add quotes to output string and convert HTML character codes to unicode w/ HTMLParser
                    irc_output = h.unescape('\"' + page_title + '\"')
                    phenny.say(irc_output)
                    page_title_len = 4 # Set test length for twitter post
                else:
                    page_title_len = 0
            except Exception, e:
                # print "No <title> tag exists in linked URL's html."
                page_title_len = 0
            ## Post link (and page title if available) to twitter account
            if "RobotoRoberto" in url: # Escape own twitter handle link
                pass
            elif page_title_len > 3 or url[-4:] in pic_exts:
                twitter_api = twitter.Api(input.twitter_consumer_key,
                                            input.twitter_consumer_secret,
                                            input.twitter_access_token_key,
                                            input.twitter_access_token_secret)
                if page_title_len == 0:
                    twitter_update = str(url)
                else:
                    twitter_update = str(url) + " - " + str(page_title)
                try:
                    twitter_api.PostUpdate(twitter_update)
                except twitter.TwitterError, e:
                    print e
    return

url_announce.rule = r'(.*?)https?://'
url_announce.name = 'url_announce'
url_announce.example = 'ted: http://www.reuters.com --> irc_bot: "Breaking News, Top News & Latest News Headlines | Reuters.com"'
url_announce.priority = 'medium'


if __name__ == "__main__":
    print __doc__.strip()