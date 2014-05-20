# try volatile function
"""
so this is an experiment that didn't work out. If you make a function volatile, then 
every function that calls it needs to be volatile (if not, then memoization means that
the volatile function won't actually be called)

I'm going to try a different approach in test8.py, using a dag.var

"""
import datetime
import time
import dag
import sys
import logging

@dag.func
def volfunc():
    return datetime.datetime.now().second

@dag.func
def foo():
    return volfunc() * 2


if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    
    for i in range(20):
        print foo()
        #print volfunc()
        time.sleep(0.3)
    