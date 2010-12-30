
from __future__ import division

import sys

from twisted.python import log
from twisted.internet.defer import Deferred
from twisted.application.app import ReactorSelectionMixin


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
        if self._finished is not None:
            self._request()

    def _stop(self, reason):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            if reason is not None:
                finished.errback(reason)
            else:
                finished.callback(self._requestCount)



PRINT_TEMPL = ('%(stats)s %(name)s/sec (%(count)s %(name)s '
              'in %(duration)s seconds)')

def benchmark_report(acceptCount, duration, name):
    print PRINT_TEMPL % {
        'stats'    : acceptCount / duration,
        'name'     : name,
        'count'    : acceptCount,
        'duration' : duration
        }



def setup_driver(f, argv, reactor, reporter):
    from twisted.python.usage import Options

    class BenchmarkOptions(Options, ReactorSelectionMixin):
        optParameters = [
            ('iterations', 'n', 1, 'number of iterations', int),
            ('duration', 'd', 5, 'duration of each iteration', float),
            ('warmup', 'w', 0, 'number of warmup iterations', int),
        ]

    options = BenchmarkOptions()
    options.parseOptions(argv[1:])
    duration = options['duration']
    jobs = [f] * options['iterations']
    d = Deferred()
    def work(res, counter):
        try:
            f = jobs.pop()
        except IndexError:
            d.callback(None)
        else:
            next = f(reactor, duration)
            if counter <= 0:
                next.addCallback(reporter, duration, f.__module__)
            next.addCallbacks(work, d.errback, (counter - 1,))
    work(None, options['warmup'])
    return d


class Driver(object):
    benchmark_report = staticmethod(benchmark_report)

    def driver(self, f, argv):
        from twisted.internet import reactor
        d = setup_driver(f, argv, reactor, benchmark_report)
        d.addErrback(log.err)
        reactor.callWhenRunning(d.addBoth, lambda ign: reactor.stop())
        reactor.run()


    def multidriver(self, *f):
        from twisted.internet import reactor
        jobs = iter(f)
        def work():
            for job in jobs:
                d = setup_driver(job, sys.argv, reactor, self.benchmark_report)
                d.addCallback(lambda ignored: work())
                return
            reactor.stop()
        reactor.callWhenRunning(work)
        reactor.run()



_driver = Driver()
driver = _driver.driver
multidriver = _driver.multidriver
del _driver
