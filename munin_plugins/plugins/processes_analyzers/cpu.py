from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE

class cpu_usage_snsr(sensor):
  sys_mtd='cpu_times'
  proc_mtd='get_cpu_times'
  
  @property
  def _env(self):
    inherit_env=super(cpu_usage_snsr,self)._env
    inherit_env.update({
      'subtitle':'CPU Usage',
      'label':'%',
      'cache':'%s/processesprocess'%CACHE,
      'graph':"AREASTACK",
    })
    return inherit_env
    
  def _evaluate(self,cache_id,curr):    
    prev=self.getValue(cache_id,curr)    
    pdff=self._mkdiff(prev,curr)          
    return self.get_percent_of(pdff,self._sysdiff()) 
