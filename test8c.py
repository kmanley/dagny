# declared at class level, these are class vars not instance properties.
# TODO: figure out if this is what we want. Is there a way to combine
# @property and dag.var? or create a dag.property class if needed...

import datetime
import time
import dag_on as dag
import sys
import logging

class Person(object):
    def __init__(self, f=None, l=None):
        self._firstname = dag.var(f)
        self._lastname = dag.var(l)
        
    @property
    def firstname(self):
        return self._firstname
    @firstname.setter
    def firstname(self, value):
        self._firstname.set(value)

    @property
    def lastname(self):
        return self._lastname.get()
    @lastname.setter
    def lastname(self, value):
        self._lastname.set(value)
        
    @property
    def fullname(self):
        return self.firstname + " " + self.lastname

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    
    p1 = Person("Kevin", "Manley")
    print p1.firstname
    #print p1.lastname
    #print p1.get_fullname()
    
    #p2 = Person("John", "Doe")
    #print p2.firstname
    #print p2.lastname
    #print p2.get_fullname()
    
    #print p1.firstname == p2.firstname
    
    
    