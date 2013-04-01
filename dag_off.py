from dag_on import DummyContextHandler
import logging
log = logging.getLogger(__name__)
log.info("dag is off")

dag = None

def set_log_level(level):
    log.setLevel(level)

def function(f=None, instmethod=False, hashargs=False):
    if f:
        return f
    else:
        def partial_wrapped_func(f):
            return function(f, instmethod, hashargs)
        return partial_wrapped_func
    
method = lambda f : function(f, instmethod=True)    
func = function
meth = method

class var(object):
    def __init__(self, value):
        self._value = value

    def get(self, caller=None):
        return self._value

    def __get__(self, obj=None, objtype=None):
        return self._value
        
    def set(self, value):
        self._value = value

    __set__ = lambda self, obj, value : self.set(value)
        
layer = lambda name: DummyContextHandler()
temp_layer = lambda : DummyContextHandler()
    
if __name__ == "__main__":        
    pass