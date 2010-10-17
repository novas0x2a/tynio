#!/usr/bin/env python

from twisted.web.http import HTTPClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from twisted.python import log as twistedLog
from urlparse import urlparse

try:
    import simplejson as json
except ImportError:
    import json

try:
    from hashlib import md5
except ImportError:
    import md5

class _CometStream(HTTPClient):
    stream = 0
    callback = None

    def sendCommand(self, command, path):
        self.transport.write('%s %s HTTP/1.1\r\n' % (command, path))

    def lineReceived(self, line):
        if not self.stream:
            if line == "":
                self.stream = 1
        else:
            try:
                if '{' in line:
                    notice = json.loads(line)
                    self.callback(notice)
                    twistedLog.msg('Got notice: %s' % notice)
            except ValueError, e:
                pass

    def connectionMade(self):
        self.sendCommand('GET', self.factory.path)
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('User-Agent', self.factory.agent)
        self.endHeaders()
        twistedLog.msg('Connected and receiving...')

class _CometFactory(ReconnectingClientFactory):
    protocol = _CometStream

    def __init__(self, callback, host, path, agent=None):
        self.callback = callback
        self.host     = host
        self.path     = path
        self.agent    = agent

    def buildProtocol(self, addr):
        p = ReconnectingClientFactory.buildProtocol(self, addr)
        p.callback = self.callback
        self.resetDelay()
        return p

    def clientConnectionLost(self, connector, reason):
        twistedLog.msg('CometStream lost!')
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

class NotifyIO(object):
    def __init__(self, listen_url, callback):
        self.callback = callback
        url = urlparse(listen_url)
        self.path = url.path
        if url.query: self.path += '?' + url.query
        self.host = url.hostname
        self.factory = _CometFactory(callback, self.host, self.path)

    def listen(self):
        reactor.connectTCP(self.host, 80, self.factory)

    def kill(self):
        self.factory.doStop()
