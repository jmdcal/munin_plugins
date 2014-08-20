"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

from munin_plugins.utils import CachePickle

from munin_plugins.plugins.plugin import SubPlugin

#Base class: used to inherit
class sensor(SubPlugin):
  sys_mtd='generic_sensor'
  proc_mtd='generic_sensor'
  id_column='id'
  
  def __init__(self,sys_prev=None,sys_curr=None):
    if sys_prev is not None and sys_curr is not None:
      self.sys_prev=sys_prev
      self.sys_curr=sys_curr
      cache_file=self.getenv('cache')
      if cache_file is not None:
        self._pcache=CachePickle(cache_file)
      else:
        self._pcache=None      
      
  def calculate(self,cache_id,curr):
    res=self._evaluate(cache_id,curr)
    
    if self._pcache is not None and curr is not None:
      if isinstance(curr,list):
        val=self._merge([self.namedtuple2dict(cv) for cv in curr],self._pcache.get(cache_id),self.id_column)
      else:
        val=self.namedtuple2dict(curr)  
        
      self.setValue(cache_id,val)
    return res
  
  def graphType(self):
    return self.getenv('graph')   
  
  def store_in_cache(self):
    if self._pcache is not None:
      self._pcache.store_in_cache()
  
  def getValue(self,key, df=None):
    res=None
    if self._pcache is not None:
      res=self._pcache.get(key,df)    
    return res
  
  def setValue(self,key,val):
    if self._pcache is not None:
      self._pcache[key]=val
  
  #To implement in derived classes
  def _evaluate(self,cache_id,curr):    
    return 0
    
  def _merge(self,main,sec,field_id):
    res={}
    if sec is not None:
      for row in sec:
        res[row.get(field_id)]=row
    if main is not None:
      for row in main:
        res[row.get(field_id)]=row
    return res.values()
 
  def _mkdiff(self,prev,curr):
    tot_c=self._mktot(curr)
    tot_p=self._mktot(prev)
    dff=tot_c-tot_p
    if dff<0:
      #the process/system was restart
      dff=tot_c
    return dff  
  
  def _sysdiff(self):
    return self._mkdiff(self.sys_prev[self.sys_mtd],self.sys_curr[self.sys_mtd])
  
  def _mktot(self,val):
    if isinstance(val,dict):
      tot=sum(val.values())  
    elif isinstance(val,tuple):
      tot=sum(val)
    elif isinstance(val,int) or isinstance(val,float):
      tot=val
    else:
      tot=0  
    return tot

  def _cut(self,val):
    parts=val.split('/')
    res='undefined'
    if len(parts)>0:
      res=parts[-1].replace('.','_')
    return res

