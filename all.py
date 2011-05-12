
from benchlib import multidriver

import iteration, names, threads, web, pb, amp
import tcp_connect, ssh_connect, ssl_connect, sslbio_connect
import tcp_throughput, ssh_throughput, ssl_throughput, sslbio_throughput
import linereceiver, lineonlyreceiver, int16receiver

allBenchmarks = [
    iteration.main, names.main, threads.main, web.main, pb.main, amp.main,
    tcp_connect.main, ssl_connect.main, sslbio_connect.main, ssh_connect.main,
    tcp_throughput.main, ssl_throughput.main, sslbio_throughput.main,
    ssh_throughput.main, linereceiver.main, lineonlyreceiver.main,
    int16receiver.main
    ]

if __name__ == '__main__':
    multidriver(allBenchmarks)
