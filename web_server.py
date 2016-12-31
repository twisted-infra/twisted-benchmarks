
"""
This benchmark runs a trivial Twisted Web server and client and makes as many
requests as it can in a fixed period of time.

A significant problem with this benchmark is the lack of persistent connections
in the HTTP client.  Lots of TCP connections means lots of overhead in the
kernel that's not really what we're trying to benchmark.  Plus lots of sockets
end up in TIME_WAIT which has a (briefly) persistent effect on system-wide
performance and makes consecutive runs of the benchmark vary wildly in their
results.
"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.defer import Deferred
from twisted.web.server import Site
from twisted.web.static import Data
from twisted.web.resource import Resource
from twisted.python.compat import networkString
from twisted.test.proto_helpers import AccumulatingProtocol

from benchlib import Client, driver


class Client(Client):
    def __init__(self, reactor, host, portNumber):
        self._endpoint = TCP4ClientEndpoint(reactor, host, portNumber)
        self._factory = Factory.forProtocol(AccumulatingProtocol)
        self._factory.protocolConnectionMade = None
        super(Client, self).__init__(reactor)


    def _request(self):
        protocols = []
        d = self._endpoint.connect(self._factory)

        @d.addCallback
        def _connected(protocol):
            protocol.closedDeferred = Deferred()

            protocol.transport.write(b"\r\n".join(b"""GET / HTTP/1.1
Host: 127.0.0.1
User-Agent: Twisted
Connection: close

""".split(b"\n")))
            protocols.append(protocol)

            return protocol.closedDeferred

        @d.addCallback
        def _finished(ign):
            protocol = protocols.pop(0)
            lines = protocol.data.split(b"\r\n")

            assert lines[0] == b"HTTP/1.1 200 OK"
            assert lines[-1] == b"Hello, world"

        d.addCallback(self._continue)
        d.addErrback(self._stop)
        return d



interface = 0
def main(reactor, duration):
    global interface
    concurrency = 10

    root = Resource()
    root.putChild(b'', Data(b"Hello, world", "text/plain"))

    interface += 1
    interface %= 255

    port = reactor.listenTCP(
        0, Site(root), backlog=128, interface='127.0.0.%d' % (interface,))

    client = Client(reactor, port.getHost().host, port.getHost().port)
    d = client.run(concurrency, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addBoth(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import web_server
    driver(web_server.main, sys.argv)
