#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
import time

def time_function(func):
    def _time_func(*args):
        t1 = time.time()
        rtn = func(*args)
        t2 = time.time()
        print(func.__name__, "took", t2-t1, "seconds to run.")
        return rtn
    return _time_func

