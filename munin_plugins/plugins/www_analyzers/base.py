from os import environ

from math import log

from collections import Counter

from munin_plugins.plugins.plugin import SubPlugin

#This class is a base for the others, do not use directly but make a subclass
class BaseCounter(SubPlugin):
  id='basecounter'
  
  def __init__(self):
    self.title='TOFIX'
    self.counter=Counter()

  def __add__(self,other):
    new=None
    if self.__class__==other.__class__:
      new=self.__class__()     
      for k,v in self.counter.items():
        new.counter[k]=v
      for k,v in other.counter.items():
        new.counter[k]=new.counter[k]+v
    else:
      raise "It's impossible to add %s object and %s object"%(self.__class__,other.__class__)
    return new
    
  def __radd__(self,other):
    new=None
    if self.__class__==other.__class__:
      new=self.__class__()
      for k,v in self.counter.items():
        new.counter[k]=v
      for k,v in other.counter.items():
        new.counter[k]=new.counter[k]+v

    else:
      raise "It's impossible to add %s object and %s object"%(self.__class__,other.__class__)
    return new
     
  def update_with(self,datas):
    pass
  
  def print_config_header(self):
    print "graph_title FIXME"
    print "graph_args --base 1000"
    print "graph_vlabel %s"%self.getenv('label')
    print "graph_category %s"%self.getenv('group')
  
  def print_data(self, printer, w=None,c=None):
    pass

  def update_cache(self):
    pass


