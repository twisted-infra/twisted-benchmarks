
"""
Evaluate one or more benchmarks and upload the results to a Speedcenter server.
"""

from __future__ import division

if __name__ == '__main__':
    from sys import argv
    from all import allBenchmarks
    from speedcenter import SpeedcenterDriver
    print SpeedcenterDriver().multidriver(allBenchmarks, argv[1:])
    raise SystemExit()

from os import uname
from sys import executable
from datetime import datetime
from urllib import urlopen, urlencode

import twisted
from twisted.python.filepath import FilePath
from twisted.python.usage import UsageError

from benchlib import BenchmarkOptions, Driver

# Unfortunately, benchmark name is the primary key for speedcenter
SPEEDCENTER_NAMES = {
    'tcp_connect': 'TCP Connections',
    'tcp_throughput': 'TCP Throughput',
    'ssh_connect': 'SSH Connections',
    'ssh_throughput': 'SSH Throughput',
    'ssl_connect': 'SSL Connections',
    'ssl_throughput': 'SSL Throughput',
    'sslbio_connect': 'SSL (Memory BIO) Connections',
    'sslbio_throughput': 'SSL (Memory BIO) Throughput',
    }


def reportEnvironment():
    revision = twisted.version.short().split('r', 1)[1]

    packageDirectory = FilePath(twisted.__file__).parent()

    try:
        import pysvn
    except ImportError:
        entries = packageDirectory.child('.svn').child('entries').getContent()
        lines = entries.splitlines()
        revision = lines[3]
        date = lines[9][:19].replace('T', ' ')
    else:
        client = pysvn.Client()
        [entry] = client.log(
            packageDirectory.path,
            pysvn.Revision(pysvn.opt_revision_kind.number, int(revision)),
            limit=1)
        date = str(datetime.fromtimestamp(entry['date']))

    return {
        'project': 'Twisted',
        'executable': executable,
        'environment': uname()[1].split('.')[0],
        'commitid': revision,
        'revision_date': date,
        'result_date': str(datetime.now()),
        }


class SpeedcenterOptions(BenchmarkOptions):
    optParameters = [
        ('url', None, None,
         'Location of Speedcenter to which to upload results.'),
        ]

    def postOptions(self):
        if not self['url']:
            raise UsageError("The Speedcenter URL must be provided.")



class SpeedcenterDriver(Driver):
    options = SpeedcenterOptions

    def __init__(self):
        super(SpeedcenterDriver, self).__init__()
        self.results = {}


    def benchmark_report(self, acceptCount, duration, name):
        self.results.setdefault(name, []).append((acceptCount, duration))


    def multidriver(self, benchmarks, argv):
        raw = super(SpeedcenterDriver, self).multidriver(benchmarks, argv)
        results = {}
        for (name, stringValue) in raw.iteritems():
            name = name.split('.')[0]
            value = eval(stringValue).values()[0]
            results[name] = value

        environment = reportEnvironment()

        for (name, values) in sorted(results.items()):
            rates = [count / duration for (count, duration) in values]
            totalCount = sum([count for (count, duration) in values])
            totalDuration = sum([duration for (count, duration) in values])

            name = SPEEDCENTER_NAMES.get(name, name)
            stats = environment.copy()
            stats['benchmark'] = name
            stats['result_value'] = totalCount / totalDuration
            stats['min'] = min(rates)
            stats['max'] = max(rates)

            # Please excuse me.
            fObj = urlopen(self.options['url'], urlencode(stats))
            print name, fObj.read()
            fObj.close()

def main(argv):
    driver = SpeedcenterDriver()
    driver.main(argv)
    print driver.results
