# motivating example
import sys
import time
#import dag_off as dag
if len(sys.argv) != 2:
    print "usage: test9 [on|off]"
    sys.exit(1)
if sys.argv[1].lower().strip() == "on":
    print "dag on"
    import dag_on as dag
else:
    print "dag off"
    import dag_off as dag
#import dag_on as dag
import logging
logging.basicConfig()

basket_spreads = {
     "LLB"  : dag.var(1.0),
     "MLB"  : dag.var(2.0),
     "SEAS" : dag.var(3.0)
}

class Benchmark(object):
    def __init__(self, name, price):
        self._name = name
        self._price = dag.var(price)
        
    @dag.meth
    def price(self):
        # simulate expensive calculation
        for i in range(1000):
            pass
        return self._price.get()    
    
class Instrument(object):
    def __init__(self, name, bmark, basket):
        self.name = name
        self.bmark = bmark
        self.basket = dag.var(basket) 
        
    @dag.meth
    def price(self):
        return self.bmark.price() + basket_spreads[self.basket.get()].get()

@dag.func    
def test():
    #dag.set_log_level(logging.DEBUG)
    bmark = Benchmark("FNCL 3.50 APR 13", 100)
    x1 = bmark.price()  # 100
    #print x
    inst = Instrument("FG A12983", bmark, "LLB")
    x2 = inst.price() # 101
    #print x
    
    #print '-' * 40
    # change the basket. With dag, benchmark price does not have to
    # be recalculated. Without dag, it does
    inst.basket.set("MLB")
    x3 = inst.price()  # 102
    #print x
        
    #print '-' * 40
    # change the spread for the basket. With dag, again the benchmark
    # price does not have to be recalc'd
    basket_spreads["MLB"].set(10)
    x4 = inst.price() # 110
    #print x
    
    #print '-' * 40
    # change the benchmark price. With dag, the spread doesn't have
    # to be recalc'd
    bmark._price.set(105)
    x5 = inst.price() # 115
    
    #print '-' * 40
    # change the spread. With dag, the benchmark price doesn't have
    # to be recalc'd
    basket_spreads["MLB"].set(2)
    x6 = inst.price() # 107
    #print x
    
    #print x
    return (x1, x2, x3, x4, x5, x6)
    
EXPECTED = (100, 101, 102, 110, 115, 107)
@dag.func
def timing_test():
    dag.set_log_level(logging.ERROR)
    ITERS = 10000
    import time
    start = time.clock()
    for i in range(ITERS):
        ret = test()
        #print ret
        assert ret == EXPECTED, "%s != %s" % (repr(ret), repr(EXPECTED))
    elapsed = time.clock() - start
    print "elapsed: %.2f secs" % elapsed
    
if __name__ == "__main__":
    #dag.set_log_level(logging.DEBUG)
    #test()
    timing_test()