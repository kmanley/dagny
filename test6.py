# trap non dag function calling dag function
import pprint
import dag
import sys
import logging

def boo(x):
    return bar(x, x*2)

@dag.function
def bar(p, q):
    return p * q

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    #log.setLevel(logging.DEBUG)
    
    boo(3)