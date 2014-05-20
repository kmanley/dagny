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
        if f:
            self.firstname = f
        if l:
            self.lastname = l
        
    firstname = dag.var("Joe")
    lastname = dag.var("Smith")
    
    @dag.method
    def get_fullname(self):
        return self.firstname + " " + self.lastname

if __name__ == "__main__":
    logging.basicConfig()
    dag.set_log_level(logging.DEBUG)
    
    p1 = Person("Kevin", "Manley")
    print p1.firstname
    print p1.lastname
    print p1.get_fullname()
    
    p2 = Person()
    print p2.firstname
    print p2.lastname
    print p2.get_fullname()
    
    print p1.firstname == p2.firstname
    
    
    