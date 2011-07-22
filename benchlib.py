from __future__ import division

import sys, subprocess

from twisted.python import log, reflect
from twisted.internet.defer import Deferred
from twisted.application.app import ReactorSelectionMixin
from twisted.python.usage import Options


class BenchmarkOptions(Options, ReactorSelectionMixin):
    optParameters = [
        ('iterations', 'n', 1, 'number of iterations', int),
        ('duration', 'd', 5, 'duration of each iteration', float),
        ('warmup', 'w', 0, 'number of warmup iterations', int),
    ]



class Client(object):
    def __init__(self, reactor):
        self._reactor = reactor
        self._requestCount = 0


    def run(self, concurrency, duration):
        self._reactor.callLater(duration, self._stop, None)
        self._finished = Deferred()
        self._finished.addBoth(self._cleanup)
        for i in range(concurrency):
            self._request()
        return self._finished


    def cleanup(self):
        pass


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


    def _cleanup(self, passthrough):
        self.cleanup()
        return passthrough



PRINT_TEMPL = ('%(stats)s %(name)s/sec (%(count)s %(name)s '
              'in %(duration)s seconds)')

def benchmark_report(acceptCount, duration, name):
    print PRINT_TEMPL % {
        'stats'    : acceptCount / duration,
        'name'     : name,
        'count'    : acceptCount,
        'duration' : duration
        }



def perform_benchmark(reactor, duration, iterations, warmup, f, reporter):
    jobs = [f] * iterations
    d = Deferred()
    def work(res, counter):
        try:
            f = jobs.pop()
        except IndexError:
            d.callback(None)
        else:
            try:
                next = f(reactor, duration)
            except:
                d.errback()
            else:
                if counter <= 0:
                    next.addCallback(reporter, duration, f.__module__)
                next.addCallbacks(work, d.errback, (counter - 1,))
    work(None, warmup)
    return d


class Driver(object):
    benchmark_report = staticmethod(benchmark_report)

    options = BenchmarkOptions

    def main(self, argv):
        benchmark = reflect.namedAny(argv[0])
        self.driver(benchmark, argv[1:])


    def driver(self, f, argv):
        self.options = self.options()
        self.options.parseOptions(argv)

        from twisted.internet import reactor

        d = perform_benchmark(
            reactor,
            self.options['duration'], self.options['iterations'],
            self.options['warmup'], f, self.benchmark_report)
        d.addErrback(log.err)
        reactor.callWhenRunning(d.addBoth, lambda ign: reactor.stop())
        reactor.run()


    def multidriver(self, benchmarks, argv):
        results = {}
        for benchmark in benchmarks:
            child = subprocess.Popen([
                    sys.executable, '-c',
                    'from sys import argv\n'
                    'from twisted.python.reflect import namedAny\n'
                    'benchlib = namedAny(argv[1])\n'
                    'benchlib.main(argv[2:])\n',
                    self.__module__, benchmark] + argv,
                                     stdout=subprocess.PIPE)
            stdout, stderr = child.communicate()
            results[benchmark] = stdout
            print 'done'
        return results


driver = Driver().driver
multidriver = Driver().multidriver
main = Driver().main
