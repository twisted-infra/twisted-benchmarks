
import sys
from twisted.internet.defer import Deferred
from twisted.internet import reactor

class Client(object):
    def __init__(self, reactor):
        self._reactor = reactor
        self._requestCount = 0


    def run(self, concurrency, duration):
        self._reactor.callLater(duration, self._stop, None)
        self._finished = Deferred()
        for i in range(concurrency):
            self._request()
        return self._finished


    def _continue(self, ignored):
        self._requestCount += 1
        self._request()


    def _stop(self, reason):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            if reason is not None:
                finished.errback(reason)
            else:
                finished.callback(self._requestCount)

def setup_driver(f, argv, reactor):
    from twisted.python.usage import Options

    class BenchmarkOptions(Options):
        optParameters = [
            ('iterations', 'n', 1, 'number of iterations', int),
        ]

    options = BenchmarkOptions()
    options.parseOptions(argv[1:])
    d = f(reactor, options['iterations'])
    return d

def driver(f, argv):
    d = setup_driver(f, argv, reactor)
    reactor.callWhenRunning(d.addBoth, lambda ign: reactor.stop())
    reactor.run()

def multidriver(*f):
    jobs = iter(f)
    def work():
        for job in jobs:
            d = setup_driver(job, sys.argv, reactor)
            d.addCallback(lambda ignored: work())
            return
        reactor.stop()
    reactor.callWhenRunning(work)
    reactor.run()
