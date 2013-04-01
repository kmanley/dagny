"""
(c) Copyright 2013 Kevin T. Manley
Any use is allowed as long as this copyright notice is kept intact.
github.com/kmanley
"""

# TODO: be able to replace lock class with nop - done, test it.
# TODO: make sure var works as class var, instance var, and module var
# TODO: layers - done
# TODO: try cycle in graph - what happens
# TODO: graph visualization, use nx graphviz support
# TODO: stats, e.g. cache hits/misses for each function
# TODO: unit tests
# TODO: document
import sys
import hashlib
import cPickle as pickle
import threading
import pprint
import networkx as nx
from functools import wraps, partial
import logging
log = logging.getLogger(__name__)
log.info("dag is on")

class Error(Exception):
    pass

def memoize(func):
    cache = {}
    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap

@memoize
def get_module_from_filename(filename):        
    """
    Given a module filename, return the corresponding 
    module handle
    """
    d = dict((m.__file__.replace('.pyc', '.py'), m) for m in \
             sys.modules.values() if hasattr(m, "__file__"))
    mod = d.get(filename)
    return mod

@memoize
def get_func_handle(mod_or_inst, func_name):
    """
    Given a module or instance and a function name, return 
    a handle to the function.
    """
    #We need to cache handles to bound methods otherwise every 
    #call to getattr can potentially return a different handle 
    return getattr(mod_or_inst, func_name, None)

@memoize
def get_calling_function(caller_self, caller_func, caller_filename):
    """
    Helper function for determining identify of caller
    """
    caller = None
    if caller_self:
        caller = get_func_handle(caller_self, caller_func)
        return caller
    else:
        caller_module = get_module_from_filename(caller_filename)
        if caller_module:
            caller = get_func_handle(caller_module, caller_func)
        return caller

def get_caller():
    """
    Gets the handle of the caller who called the function that
    called us.
    """
    caller_frame = sys._getframe(2)
    caller = get_calling_function(caller_frame.f_locals.get('self'), 
                                  caller_frame.f_code.co_name,
                                  caller_frame.f_code.co_filename)
    return caller

def set_log_level(level):
    """
    Sets logging level for this module
    """
    log.setLevel(level)

def nx_iter_successors(graph, node):
    """
    Helper for networkx which recursively
    yields successors of node in graph.
    """
    if node in graph:
        for item in graph.successors_iter(node):
            yield item
            for subitem in nx_iter_successors(graph, item):
                yield subitem

def nx_iter_predecessors(graph, node):
    """
    Helper for networkx which recursively
    yields predecessors of node in graph.
    """
    if node in graph:
        for item in graph.predecessors_iter(node):
            yield item
            for subitem in nx_iter_predecessors(graph, item):
                yield subitem            
                
class DummyContextHandler(object):
    """
    Do-nothing context handler used when thread safety is turned off
    """
    def __init__(self, *args):
        pass
    def __enter__(self):
        return self
    def __exit__(self, t, v, tb):
        pass
                
class Dag(object):
    """
    Dag class. The only instance should be the singleton 
    in this module.
    """
    def __init__(self):
        self._graph = nx.DiGraph()
        self._layer = None
        self._lock = None
        self.set_thread_safety(True)
        self._memo = {} # layer -> {func -> {args : result}}
        self.set_layer()
        
    def get_layers(self):
        with self._lock:
            return self._memo.keys()
        
    def set_layer(self, name=None):
        log.debug("setting layer to %s" % name)
        with self._lock:
            self._layer = name
            self._memo.setdefault(name, {})
            
    def pop_layer(self, name):
        log.debug("popping layer %s" % name)
        if not name:
            return
        with self._lock:
            self._memo.pop(name, None)
        
    def set_thread_safety(self, threadsafe=True):
        """
        Turns thread-safety on or off. Thread safety
        incurs a slight locking overhead
        """
        if threadsafe:
            self._lock = threading.RLock()
        else:
            self._lock = DummyContextHandler()

    @staticmethod
    def get_memo_key(args, kwargs, hashargs):
        """
        Given args, kwargs produce a stable key for
        the memoization dict. If hashargs is True, hash
        the args. hashargs should only be used if args
        and kwargs are very large data structures
        """
        memokey = args + tuple(sorted(kwargs.items()))
        if hashargs:
            memokey = hashlib.sha256(pickle.dumps(memokey))
        return memokey
        
    def get_memo(self, func, key):
        """
        Fetch a value from memoization dict. Raises
        KeyError if key is not in the dict
        """
        log.debug("get_memo(%s, %s, %s)" % (self._layer, func, key))
        with self._lock:
            return self._memo[self._layer][func][key]
        
    def set_memo(self, func, key, value):
        """
        Sets a key/value pair in the memoization dict
        """
        log.debug("set_memo(%s, %s, %s, %s)" % (self._layer, func, repr(key), repr(value)))
        with self._lock:            
            self._memo[self._layer].setdefault(func, {})[key] = value

    def clear_memo(self, func):
        """
        Clears the memoization dict for a specific function
        """
        log.debug("clear_memo(%s, %s)" % (self._layer, func))
        with self._lock:
            self._memo[self._layer][func] = {}

    def invalidate_parents(self, func):
        """
        Invalidates all parent nodes of func. That is, all 
        the functions that depend on func.
        """
        with self._lock:
            for parentfunc in self.iter_parents(func):
                self.clear_memo(parentfunc)
        
    def has_dependency(self, caller, this_func):
        """
        Returns True if caller depends on this_func
        """
        with self._lock:
            return self._graph.has_edge(caller, this_func)
        
    def add_dependency(self, caller, this_func):
        """
        Adds a dependency from caller to this_func 
        to the dependency graph
        """
        # caller can be None if calling code is from top-level __main__ module
        if caller:
            if not dag.has_dependency(caller, this_func):
                # we aren't already tracking this dependency, so add it now
                try:
                    caller._on_dag
                except AttributeError:
                    raise Error("non-dag fn %s makes a runtime call to dag fn %s" 
                                " (are you missing a @dag.func or @dag.meth decorator on %s?)" % \
                                (caller, this_func, caller))                    
                log.debug("%s (0x%x) depends on\n    %s (0x%x)" % (caller, id(caller), this_func, id(this_func)))
                with self._lock:
                    self._graph.add_edge(caller, this_func)
            
    def iter_children(self, node):
        """
        Returns all children of node. That is, all
        functions on which node depends.
        """
        with self._lock:
            return nx_iter_successors(self._graph, node)

    def iter_parents(self, node):
        """
        Returns all parents of node. That is, all
        functions which depend on node.
        """
        with self._lock:
            return nx_iter_predecessors(self._graph, node)
        
    def dump_graph(self):
        with self._lock:
            pprint.pprint(self._graph.edges())
        
dag = Dag()        
        
def function(f=None, instmethod=False, hashargs=False): 
    """
    Decorator for functions you want included on the dag.
    Note: this is for plain functions. For class/instance
    methods please use the method decorator instead.
    """
    if f:
        @wraps(f)
        def wrapped_func(*args, **kwargs):
            caller = get_caller()
            if instmethod:
                this_func = get_func_handle(args[0], f.__name__)
            else:
                this_func = get_func_handle(sys.modules[f.__module__], f.__name__)

            dag.add_dependency(caller, this_func)
            memokey = dag.get_memo_key(args, kwargs, hashargs)
            #result = -9999999 # TODO:
            try:
                result = dag.get_memo(this_func, memokey)
                log.debug("cache HIT %s(%s)->%s" % (this_func, memokey, result))
                #return result
            except KeyError:
                log.debug("cache MISS %s(%s)" % (this_func, memokey))
                result = f(*args, **kwargs)
                dag.set_memo(this_func, memokey, result)
            return result
            #finally:
            #    return result
        wrapped_func._on_dag = True
        #wrapped_func.__name__ = "%s_wrapped" % f.__name__ # TODO:
        return wrapped_func
    else:
        def partial_wrapped_func(f):
            return func(f, instmethod, hashargs) 
        return partial_wrapped_func

func = function

method = lambda f : function(f, instmethod=True)    
meth = method

class var(object):
    """
    Dag variable. These are always the terminal nodes of the
    graph, with functions depending on their values.
    
    This class can be used as a standalone var or as an 
    instance variable, in which case the descriptor protocol
    methods are used. 
    """
    def __init__(self, value):
        log.debug("%s.__init__(%s)" % (self, repr(value)))
        self._value = value

    def get(self, caller=None):
        log.debug("%s.get -> %s" % (self, repr(self._value)))
        caller = caller or get_caller()
        this_func = get_func_handle(self, "get")
        dag.add_dependency(caller, this_func)
        return self._value

    def __get__(self, obj=None, objtype=None):
        return self.get(caller=get_caller())
    __get__._on_dag = True
        
    def set(self, value):
        if value == self._value:
            log.debug("ignoring %s.set(%s)" % (self, repr(value)))
            return # nothing to do
        log.debug("%s.set(%s)" % (self, repr(value)))
        self._value = value
        getfn = get_func_handle(self, 'get')
        dag.invalidate_parents(getfn)

    __set__ = lambda self, obj, value : self.set(value)
        
class LayerContextHandler(object):
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        dag.set_layer(self.name)
        return self
    def __exit__(self, t, v, tb):
        dag.set_layer(None)
    
class TempLayerContextHandler(object):
    def __init__(self):
        self.name = "temp_%d" % (len(dag._memo)+1)
    def __enter__(self):
        dag.set_layer(self.name)
    def __exit__(self, t, v, tb):
        dag.pop_layer(self.name)
        dag.set_layer(None)

layer = lambda name: LayerContextHandler(name)
temp_layer = lambda : TempLayerContextHandler()
    
if __name__ == "__main__":        
    pass
