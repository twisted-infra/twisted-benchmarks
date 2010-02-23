
from __future__ import division

from twisted.python.log import err
from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred

from benchlib import Client, driver


class Client(Client):
    def _request(self):
        d = deferToThread(lambda: None)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def report(requestCount, duration):
    print '%s req/sec (%s thread calls in %s seconds)' % (
        requestCount / duration, requestCount, duration)



def main(reactor, iterations):
    duration = 5 * iterations
    concurrency = 10

    client = Client(reactor)
    d = client.run(concurrency, duration)
    d.addCallbacks(report, err, callbackArgs=(duration,))
    return d



if __name__ == '__main__':
    import sys
    driver(main, sys.argv)
