from collections import deque

from munin_plugins.utils import CACHE
from munin_plugins.utils import get_percent_of
from munin_plugins.utils import namedtuple2dict

#Base class: used to inherit
class sensor(object):
  id='generic_sensor'
  label='generic_sensor'
  cache=None
  sys_mtd='generic_sensor'
  proc_mtd='generic_sensor'
  graph=None
  
  def __init__(sys_prev,sys_curr):
    self.sys_prev=sys_prev
    self.sys_curr=sys_curr
    self.pcache=CachePickle(cache)

  def calculate(cache_id,curr):
    res=self.evaluate(cache_id,curr)
    if isinstance(curr,list):
      pcache[name]=self._merge([namedtuple2dict(cv) for cv in curr],self.pcache[cache_id],'id')
    else:
      pcache[name]=namedtuple2dict(curr)  
    return res
  
  def graphType():
    return self.graph   
  
  def store_in_cache():
     self.pcache.store_in_cache()
  
  #To implement in derived classes
  def _evaluate(cache_id,curr):    
    return 0
  
  def _merge(main,sec,field_id):
    res={}
    if sec is not None:
      for row in sec:
        id=row.get(field_id)
        res[id]=row
    if main is not None:
      for row in main:
        id=row.get(field_id)
        res[id]=row
    return res.values()
 
  def _mkdiff(prev,curr):
    tot_c=self._mktot(curr)
    tot_p=self._mktot(prev)
    dff=tot_c-tot_p
    if dff<0:
      #the process/system was restart
      dff=tot_c
    return dff  
  
  def _sysdiff():
    return self._mkdiff(self.sys_prev[self.sys_mtd],self.sys_curr[self.sys_mtd])
  
  def _mktot(val):
    if isinstance(val,dict):
      tot=sum(val.values())  
    elif isinstance(val,tuple):
      tot=sum(val)
    elif isinstance(val,int) or isinstance(val,float):
      tot=val
    else:
      tot=0  
    return tot

  def _cut(val):
    parts=val.split('/')
    res='undefined'
    if len(parts)>0:
      res=parts[-1].replace('.','_')
    return res

  