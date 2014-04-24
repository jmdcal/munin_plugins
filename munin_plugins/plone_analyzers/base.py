from ..utils import CachePickle
from ..utils import namedtuple2dict

#Base class: used to inherit
class sensor(object):
  label='generic_sensor'
  cache=None
  sys_mtd='generic_sensor'
  proc_mtd='generic_sensor'
  graph=None
  id_column='id'
  
  def __init__(self,sys_prev,sys_curr):
    self.sys_prev=sys_prev
    self.sys_curr=sys_curr
    self._pcache=CachePickle(self.cache)

  def calculate(self,cache_id,curr):
    res=self._evaluate(cache_id,curr)
    
    if self.cache is not None and curr is not None:
      if isinstance(curr,list):
        val=self._merge([namedtuple2dict(cv) for cv in curr],self._pcache.get(cache_id),self.id_column)
      else:
        val=namedtuple2dict(curr)  
        
      self.setValue(cache_id,val)
    return res
  
  def graphType(self):
    return self.graph   
  
  def store_in_cache(self):
     self._pcache.store_in_cache()
  
  def getValue(self,key, df=None):
    return self._pcache.get(key,df)
  
  def setValue(self,key,val):
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

  