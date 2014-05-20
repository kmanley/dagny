from test import MyClass, gvar
import dag, logging

def foo():
    dag.set_log_level(logging.DEBUG)
    m = MyClass()
    print m.mbaz(2,2)
    #m.baz = 3
    #m.x = 5
    
    #print dir(MyClass)
    
    #gvar.set(21)
    #print m.baz(2,2)
    
    
    # TODO: find a way to prevent someone clobbering a dag.func, e.g. by setting inst.fuz = 3
    #f.f_locals.get('self')
    #f.f_code.co_name # calling function name, could be '<module>' TODO: what if called from a different module?

foo()

    
