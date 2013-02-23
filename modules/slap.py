#!/usr/bin/env python
"""
slap.py - Phenny Slap Module

http://inamidst.com/phenny/
"""

def slap(phenny, input):
	for channel in phenny.channels:
		if input.sender in channel.split(" ", 1):
			if input.nick.lower() == '01010101':
				output_message = "slaps " + input.nick + "!"
				phenny.me(output_message)
	return
slap.event = 'PRIVMSG'
slap.rule = r'.*'
slap.name = 'slap'
slap.example = 'roberto slaps ralph!'
slap.priority = 'medium'

if __name__ == "__main__":
    print __doc__.strip()