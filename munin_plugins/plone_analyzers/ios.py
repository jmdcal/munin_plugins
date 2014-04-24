from .base import sensor
from ..env import CACHE
from ..utils import namedtuple2dict
  
class io_counters_snsr(sensor):
  label='I/O usage'
  cache='%s/zopeios'%CACHE
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{}) 
    res=()
    if curr is not None:
      res=[(k,self._mkdiff(prev.get(k,0),v)) for k,v in namedtuple2dict(curr).items()]
    elif prev is not None:
      res=[(i,0) for i in prev.keys()]
      
    return res
  