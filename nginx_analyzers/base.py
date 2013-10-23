
#This class is a base for the others, do not use directly but make a subclass
class BaseCounter(object):
  id='basecounter'

  def __init__(self,title,group):
    self.title=title
    self.group=group
    self.label="Base class"

  def update_with(self,datas):
    pass
  
  def print_config_header(self):
    print "graph_title %s"%self.title
    print "graph_args --base 1000"
    print "graph_vlabel %s"%self.label
    print "graph_category %s"%self.group
  
  def print_data(self, printer):
    pass

  def update_cache(self):
    pass
