from collections import deque

from munin_plugins.plugins.processes_analyzers.base import sensor
   
class connections_snsr(sensor):
  label='connections'
  cache=None
  sys_mtd='connections'
  proc_mtd='get_connections'
  _properties={}
  
  def _evaluate(self,cache_id,curr):
    res=0
    try:
      res=len(curr)
    except:
      pass
    return res 

  