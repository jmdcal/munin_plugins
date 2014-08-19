from collections import deque

from munin_plugins.plugins.processes_analyzers.base import sensor
   
class connections_snsr(sensor):
  sys_mtd='connections'
  proc_mtd='get_connections'
  
  @property
  def _env(self):
    inherit_env=super(connections_snsr,self)._env
    inherit_env.update({
      'subtitle':'Network Connections',
      'label':'number',
    })
    return inherit_env  
  
  def _evaluate(self,cache_id,curr):
    res=0
    try:
      res=len(curr)
    except:
      pass
    return res 

  