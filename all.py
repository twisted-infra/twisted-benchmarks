
from benchlib import multidriver

import accepts, tcp, iteration, names, threads, web, pb, amp
import ssh_connect, ssh_throughput

allBenchmarks = [
    accepts.main, tcp.main, iteration.main, names.main, threads.main,
    web.main, pb.main, amp.main, ssh_connect.main, ssh_throughput.main]

if __name__ == '__main__':
    multidriver(allBenchmarks)
