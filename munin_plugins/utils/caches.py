"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import time
import fcntl
import pickle
from base64 import b64encode
from base64 import b64decode

from collections import Counter
from collections import deque

from os.path import isfile

#Base Cache Class
class _Cache(object): 
  default=None
  
  def __init__(self,fn,def_value=None,*args,**kargs):
    super(_Cache,self).__init__(*args,**kargs)
    self.fn=fn       
    if def_value is not None:
      self.default=def_value
    self.load_from_cache()
    
  def _lock(self,fd):
    locked=False
    while not locked:
      try:
        fcntl.lockf(fd,fcntl.LOCK_EX)
      except IOError:
        time.sleep(3)
      else:
        locked=True
    
  def _unlock(self,fd):  
    fcntl.lockf(fd, fcntl.LOCK_UN)

  def load_from_cache(self):
    if self.fn is not None and isfile(self.fn):
      fd=open(self.fn,'r')
      for i in fd:
        i=i.strip()
        if len(i)>0:
          self.load_value(i)
      fd.close()

  def store_in_cache(self):   
    if self.fn is not None:
      fd=open(self.fn,'w')    
      self._lock(fd)
                   
      #now in values we have only new values for cache and we will append to file
      for l in self.get_values():
        fd.write('%s\n'%l)
        
      self._unlock(fd)
      fd.close()

  #Methods to define in class
  def load_value(self,val):
    pass

  def get_values(self):
    return []

#Simple cache based on a list of values
class CacheDict(_Cache,dict):  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()

#Simple cache based on a Counter, a dictionary val: qty
class CacheCounter(_Cache,Counter):    
  default=0
  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()

class CachePickle(_Cache,dict):
  default=()
  
  def load_value(self,val):
    try:
      id,pickled=val.split(' ')
      self[id]=pickle.loads(b64decode(pickled))  
    except:
      self[val]=self.default

  def get_values(self):
    res=deque()
    for k,data in self.items():
      pickled=b64encode(pickle.dumps(data))
      res.append("%s %s"%(k,pickled))
    return res
    
    
    
