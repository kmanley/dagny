import datetime
import time
import dag_off as dag
import sys
import logging

class Person(object):
    #x = dummy()
    def __init__(self):
        #self.firstname = dag.var("Kevin")
        #self.lastname = dag.var("Manley")
        #self.x = dummy()
        pass
    
    firstname = dag.var("Joe")
    lastname = dag.var("Smith")

    #@property
    #def firstname(self):
        #return self._firstname()
    
    #@firstname.setter
    ##@dag.method
    #def firstname(self, val):
        #self._firstname.set(val)
     
    ##lastname = property(self._lastname.get, self._lastname.set)
 
    #@property
    #@dag.method
    #def fullname(self):
        #return self.firstname + self.lastname
    
    @dag.method
    def get_fullname(self):
        return self.firstname + " " + self.lastname

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    
    p = Person()
    p.firstname = "Kevin"
    print "first", p.firstname
    p.lastname = "Manley"
    print "last", p.lastname
    
    #print '*' * 40
    #print p.firstname
    #print p.firstname
    #print '*' * 40
    
    #print "firstname is None? %s" % (p.firstname is None)
    #print "lastname is None? %s" % (p.lastname is None)
    
    print '-' * 40
    print p.get_fullname()
    
#    print '-' * 40
#    print p.get_fullname()
    
    print '-' * 40
    p.firstname = "Magnus"
    print p.get_fullname()
    
    print '-' * 40
    print p.get_fullname()
#    print p.firstname
#    print p.lastname
    
    
    #print p.x