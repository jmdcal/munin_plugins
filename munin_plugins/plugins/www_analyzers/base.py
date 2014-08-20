"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

from collections import Counter

from munin_plugins.plugins.plugin import SubPlugin

#This class is a base for the others, do not use directly but make a subclass
class BaseCounter(SubPlugin):
  id='basecounter'
  
  def __init__(self):
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
  
  def print_config_header(self,main_title):
    print "graph_title %s %s" % (main_title,self.getenv('subtitle'))
    print "graph_args --base 1000"
    print "graph_vlabel %s"%self.getenv('label')
    print "graph_category %s"%self.getenv('group')
  
  def print_data(self, printer, w=None,c=None):
    pass

  def update_cache(self):
    pass


