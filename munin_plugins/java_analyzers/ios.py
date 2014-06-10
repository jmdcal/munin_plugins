from .base import sensor
from ..env import CACHE
from ..utils import namedtuple2dict
  
class io_counters_snsr(sensor):
  label='I/O usage (byte of operations)'
  cache='%s/javaiosbytes'%CACHE
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{}) 
    res=()
    if curr is not None:
      res=[(k,self._mkdiff(prev.get(k,0),v)) for k,v in namedtuple2dict(curr).items() if '_bytes' in k]
    elif prev is not None:
      res=[(i,0) for i in prev.keys() if '_bytes' in i]
      
    return res

class io_counters_abs_snsr(sensor):
  label='I/O usage (# of operations)'
  cache='%s/javaiosabs'%CACHE
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{}) 
    res=()
    if curr is not None:
      res=[(k,self._mkdiff(prev.get(k,0),v)) for k,v in namedtuple2dict(curr).items() if '_count' in k]
    elif prev is not None:
      res=[(i,0) for i in prev.keys() if '_count' in i]
      
    return res

  
  