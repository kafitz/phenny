#!/usr/bin/env python
"""
telnet.py - Phenny Telnet Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Kyle Fitzsimmons 2013, kylefitz.com
"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

class Relay(Protocol):
    def dataReceived(self, data):
        """
        Given data, relay to phenny for processing
        """
        self.factory.phenny.msg("#opptest", str(data))

class RelayFactory(Factory):
    protocol = Relay

    def __init__(self, phenny):
        self.phenny = phenny

def telnet(phenny, input): 
    factory = RelayFactory(phenny)
    reactor.listenTCP(5656, factory, interface="localhost")
    # Suppress twisted catches like ctrl-c since not being run in main (phenny) thread
    reactor.run(installSignalHandlers=0)

telnet.event = '366'
telnet.rule = r'(.*)'
telnet.thread = True
telnet.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()