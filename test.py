#import networkx
import pprint
import dag
import sys
import logging

gvar = dag.var(20)

@dag.function
def foo(a, b, c):
    x = a * b + c - bar()
    
@dag.function
def bing(l):
    f = sys._getframe(1) #co_flags 67
    return l * 3
    
@dag.function
def bar(p, q):
    f = sys._getframe(1)
    return p * q * bing(p)


class MyClass(object):
    def __init__(self):
        self._x = 3
        
    @dag.meth
    def mbaz(self, arg1, arg2):
        f = sys._getframe(1)
        return self.mfuz(arg1, arg2) + bar(arg1, arg2)
        
    @dag.meth
    def mfuz(self, p1, p2):
        f = sys._getframe(1)
        return p1 - p2 * gvar.get()
    
    """
    @property
    @dag.func
    def x(self):
        return self._x

    @x.setter
    @dag.func
    def x(self, n):
        self._x = n
    """ 
        
#gvar = dag.var(20)

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    #log.setLevel(logging.DEBUG)
    
    m = MyClass()
    print m.mbaz(2,2)
    
    print '-' * 40
    
    gvar.set(21)
    print m.mbaz(2,2)
    #print "mfuz", m.mfuz(2,2)
    #print "bar", bar(1,1)
    
    import sys
    sys.exit(0)
    
    #import test2
    #test2.foo()

    
    #m.baz = 3
    #m.x = 5
    
    #print dir(MyClass)
    
    #gvar.set(21)
    #print m.baz(2,2)
    
    
    # TODO: find a way to prevent someone clobbering a dag.func, e.g. by setting inst.fuz = 3
    #f.f_locals.get('self')
    #f.f_code.co_name # calling function name, could be '<module>' TODO: what if called from a different module?
    
    print '-' * 40
    print "dumping dag:"
    dag.dag.dump()

    print '-' * 40
    #pprint.pprint(list(dag.dag.iter_children(dag.cache_func_handle(m, 'mbaz'))))
    #pprint.pprint(list(dag.dag.iter_parents(dag.get_func_handle(sys.modules["__main__"], "bing"))))
    #pprint.pprint(list(dag.dag.iter_children(dag.get_func_handle(sys.modules["__main__"], "bar"))))
    #pprint.pprint(list(dag.dag.iter_children(dag.get_func_handle(MyClass, 'mbaz'))))
    
    pprint.pprint(dag.get_func_handle(m, 'mbaz')._memo)