
from twisted.python.log import err
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred


class Client(object):
    def __init__(self, reactor):
        self._reactor = reactor
        self._requestCount = 0


    def run(self, duration):
        self._reactor.callLater(duration, self._stop, None)
        self._request()
        self._finished = Deferred()
        return self._finished


    def _request(self):
        d = deferToThread(lambda: None)
        d.addCallback(self._continue)
        d.addErrback(self._stop)


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



def report(requestCount, duration):
    print '%s req/sec (%s thread calls in %s seconds)' % (
        requestCount / duration, requestCount, duration)



def main():
    duration = 5
    client = Client(reactor)
    d = client.run(duration)
    d.addCallbacks(report, err, callbackArgs=(duration,))
    d.addCallback(lambda ign: reactor.stop())
    reactor.run()



if __name__ == '__main__':
    main()
