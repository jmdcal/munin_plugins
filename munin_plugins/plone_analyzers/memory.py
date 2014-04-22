from collections import deque

from munin_plugins.etc.env import CACHE
from munin_plugins.plone_analyzers.base import sensor
  
class memory_snsr(sensor):
  label='memory (%)'
  cache=None
  sys_mtd='memory_percent'
  proc_mtd='get_memory_percent'
  graph="AREASTACK"
  
  def _evaluate(self, cache_id,curr):
    if curr is None:
      curr=0    
    return curr
  