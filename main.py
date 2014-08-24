'''
import pentai.t_all as t_m
t_m.main()
import sys
sys.exit(0)
'''

import sys

def setup_logging():
    formatter = logging.Formatter("[%(asctime)s.%(msecs)03d][%(levelname)s][%(message)s]",
                                          "%H:%M:%S")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    sys._kivy_logging_handler = console
    sys.setrecursionlimit(500)

    logging.getLogger("ZODB.FileStorage").addHandler(console)
    logging.getLogger("ZODB.lock_file").addHandler(console)
    logging.getLogger("ZODB.Connection").addHandler(console)

def main():
    setup_logging()
    import startup
    startup.run()

import logging, sys

if __name__ == "__main__":
    '''
    import pstats, cProfile
    cProfile.runctx("main()", globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("cumulative").print_stats(20) # or "time"
    #s.strip_dirs().sort_stats("time").print_stats(20)
    '''

    main()

