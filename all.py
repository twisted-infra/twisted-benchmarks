
from benchlib import multidriver

import accepts, tcp, iteration, names, threads, web, pb, amp

allBenchmarks = [
    accepts.main, tcp.main, iteration.main, names.main, threads.main,
    web.main, pb.main, amp.main]

if __name__ == '__main__':
    multidriver(allBenchmarks)
