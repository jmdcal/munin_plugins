from collections import deque

from munin_plugins.plone_analyzers.base import sensor

from munin_plugins.etc.env import CACHE
from munin_plugins.utils import namedtuple2dict
  
class io_counters_snsr(sensor):
  label='I/O usage'
  cache='%s/zopeios'%CACHE
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{})    
    return [(k,self._mkdiff(prev.get(k,0),v)) for k,v in namedtuple2dict(curr).items()]
  