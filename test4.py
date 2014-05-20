import dag
import logging

class A(object):
  def __init__(self):
      self._cobj = C(1)

  @dag.method
  def mafoo(self):
      return 2 * self._cobj.mcfoo()

class B(object):
  def __init__(self):
      self._cobj = C(2)

  @dag.method
  def mbfoo(self):
      return 3 * self._cobj.mcfoo()

      
class C(object):
  def __init__(self, x):
      self._x = dag.var(x)

  @dag.method
  def mcfoo(self):
      return self._x()
      
if __name__ == "__main__":
  logging.basicConfig()
  dag.set_log_level(logging.DEBUG)
  a, b = A(), B()
  a.mafoo()      
  print '-' * 40
  b.mbfoo()