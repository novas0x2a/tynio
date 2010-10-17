#!/usr/bin/env python

import tynio
import pynotify

from twisted.python import log as twistedLog
from twisted.internet import reactor

# Replace with the contents of your .ListenURL file
LISTEN_URL = 'http://listen.notify.io/~1/listen/XXX'

class Notifier(object):
    ''' A small wrapper around libnotify. Because it has a crappy API. '''
    def __init__(self, app_name):
        if not pynotify.init(app_name):
            raise Exception('Failed to init pynotify')
    def notify(self, note):
        n = pynotify.Notification(note.get('title', ''), note['text'])
        if note.get('sticky', False):
            n.set_timeout(pynotify.EXPIRES_NEVER)
        n.show()

if __name__ == '__main__':
    import sys
    twistedLog.startLogging(sys.stdout)

    n = Notifier('NIO Linux Client')

    nio = tynio.NotifyIO(LISTEN_URL, n.notify)
    nio.listen()
    reactor.run()
