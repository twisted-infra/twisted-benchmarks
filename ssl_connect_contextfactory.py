"""
Pathological case similar to connecting to many hosts, regenerating the
CertificateOptions repeatedly.
"""

from time import time
from benchlib import driver

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import SSL4ServerEndpoint, SSL4ClientEndpoint

from ssl_throughput import cert
from tcp_connect import CloseConnection, Client


class WriteOneByte(Protocol):
    def connectionMade(self):
        self.transport.write(b"x")


class Client(Client):
    protocol = WriteOneByte

    def _request(self):
        factory = Factory()
        factory.protocol = self.protocol

        d = self._server().connect(factory)
        d.addCallback(self._continue)
        d.addErrback(self._stop)


def main(reactor, duration):
    concurrency = 50

    interface = '127.0.0.%d' % (int(time()) % 254 + 1,)

    factory = Factory()
    factory.protocol = CloseConnection
    serverEndpoint = SSL4ServerEndpoint(
        reactor, 0, cert.options(), interface=interface
    )

    listen = serverEndpoint.listen(factory)

    def cbListening(port):
        server = lambda: SSL4ClientEndpoint(
            reactor,
            interface,
            port.getHost().port,
            cert.options(),
            bindAddress=(interface, 0),
        )
        client = Client(reactor, server)
        d = client.run(concurrency, duration)

        def cleanup(passthrough):
            d = port.stopListening()
            d.addCallback(lambda ignored: passthrough)
            return d

        d.addCallback(cleanup)
        return d

    listen.addCallback(cbListening)
    return listen


if __name__ == '__main__':
    import sys
    import ssl_connect_contextfactory

    driver(ssl_connect_contextfactory.main, sys.argv)
