#!/usr/bin/env python
"""
wiktionary.py - Phenny Wiktionary Module
Copyright 2009, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

def log(phenny, input):
	print input.sender + " <" + input.nick + "> " + input + "\n"
log.rule = r'(?i).*'
log.priority = 'high'

if __name__ == "__main__":
    print __doc__.strip()