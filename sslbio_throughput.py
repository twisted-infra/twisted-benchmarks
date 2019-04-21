from ssl_throughput import main as _main
from sslbio_connect import SSLBIOReactor

from benchlib import driver


def main(reactor, duration):
    return _main(SSLBIOReactor(reactor), duration)


if __name__ == '__main__':
    import sys
    import sslbio_throughput

    driver(sslbio_throughput.main, sys.argv)
