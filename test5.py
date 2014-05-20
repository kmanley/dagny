# test caching the dependency calculation
import pprint
import dag
import sys
import logging

   
@dag.function
def bar(p, q):
    return p * q

class MyClass(dag.obj):
    def __init__(self):
        self._x = 3
        
    @dag.meth
    def mbaz(self, arg1, arg2):
        f = sys._getframe(1)
        return self.mfuz(arg1, arg2) * 3 #+ bar(arg1, arg2)
        
    @dag.meth
    def mfuz(self, p1, p2):
        return p1 - p2 * gvar()
    
gvar = dag.var(20)    

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    #log.setLevel(logging.DEBUG)
    
    m = MyClass()
    print m.mbaz(2,2)
    #print '-' * 40
    #print m.mbaz(4,3)
    