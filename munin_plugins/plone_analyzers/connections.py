from collections import deque

from munin_plugins.plone_analyzers.base import sensor
   
class connections_snsr(sensor):
  label='connections'
  cache=None
  sys_mtd='connections'
  proc_mtd='get_connections'
  
  def _evaluate(self,cache_id,curr):
    return len(curr)

  