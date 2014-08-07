from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE
  
class threads_snsr(sensor):
  label='threads #'
  sys_mtd='cpu_times'
  proc_mtd='get_threads'
  id_column="id"
  _defaults={
    'cache':'%s/processesthreads'%CACHE,
    'graph':'AREASTACK',
  }

  def _evaluate(self,cache_id,curr):              
    res=0
    if curr is not None:
      res=len(curr)
      
    return res

  
