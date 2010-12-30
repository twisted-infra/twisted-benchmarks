
"""
Evaluate one or more benchmarks and upload the results to a Speedcenter server.
"""

from os import uname
from sys import executable
from datetime import datetime

import pysvn

import twisted

from all import allBenchmarks
from benchlib import Driver


class SpeedcenterDriver(Driver):
    def benchmark_report(self, acceptCount, duration, name):
        self.results.append((acceptCount, duration, name))



def reportEnvironment():
    version = twisted.version.short().split('r', 1)[1]

    client = pysvn.Client()
    [entry] = client.log(wc, pysvn.Revision(pysvn.opt_revision_kind.number, revision), limit=1)
    date = str(datetime.datetime.fromtimestamp(entry['date']))

    return {
        'project': 'Twisted',
        'executable': executable,
        'environment': uname()[1],
        'commitid': version,
        'revision_date': date,

        'benchmark': None,
        'result_value': None,
        'result_date': None,
        'std_dev': None,
        'min': None,
        'max': None,
        }



def main():
    driver = SpeedcenterDriver()
    driver.results = []
    driver.multidriver(*allBenchmarks)

    environment = reportEnvironment()

    for (acceptCount, duration, name) in driver.results:
        stats = environment.copy()
        stats['benchmark'] = name
        stats['result_value'] = acceptCount / duration
        stats['result_date'] = datetime.datetime.now(),
