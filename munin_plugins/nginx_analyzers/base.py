from collections import Counter


#This class is a base for the others, do not use directly but make a subclass
class BaseCounter(object):
  id='basecounter'
  base_title="Base class"

  def __init__(self,title,group):
    self.title=title
    self.group=group
    self.label="Base class"
    self.counter=Counter()

  def __add__(self,other):
    new=None
    if self.__class__==other.__class__:
      new=self.__class__(self.title,self.group)     
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
      new=self.__class__(self.title,self.group)
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
    print "graph_title %s: %s"%(self.base_title,self.title)
    print "graph_args --base 1000"
    print "graph_vlabel %s"%self.label
    print "graph_category %s"%self.group
  
  def print_data(self, printer, w=None,c=None):
    pass

  def update_cache(self):
    pass
