from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE
  
class threads_snsr(sensor):
  sys_mtd='cpu_times'
  proc_mtd='get_threads'
  id_column="id"
  
  @property
  def _env(self):
    inherit_env=super(threads_snsr,self)._env
    inherit_env.update({
      'subtitle':'Threads',
      'label':'number',
      'cache':'%s/processesthreads'%CACHE,
      'graph':'AREASTACK',
    })
    return inherit_env
  
  def _evaluate(self,cache_id,curr):              
    res=0
    if curr is not None:
      res=len(curr)
      
    return res

  
