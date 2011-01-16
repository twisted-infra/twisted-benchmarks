
from benchlib import multidriver

import accepts, tcp, iteration, names, threads, web, pb, amp, ssh_connect

allBenchmarks = [
    accepts.main, tcp.main, iteration.main, names.main, threads.main,
    web.main, pb.main, amp.main, ssh_connect.main]

if __name__ == '__main__':
    multidriver(allBenchmarks)
