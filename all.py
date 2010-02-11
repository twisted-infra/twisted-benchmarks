
from benchlib import multidriver

import accepts, iteration, names, threads, web

if __name__ == '__main__':
    multidriver(
        accepts.main, iteration.main, names.main, threads.main, web.main)
