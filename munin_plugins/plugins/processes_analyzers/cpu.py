from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE

class cpu_usage_snsr(sensor):
  label='cpu usage (%)'
  sys_mtd='cpu_times'
  proc_mtd='get_cpu_times'
  _defaults={
    'cache':'%s/processesprocess'%CACHE,
    'graph':"AREASTACK",
  }
  
  def _evaluate(self,cache_id,curr):    
    prev=self.getValue(cache_id,curr)    
    pdff=self._mkdiff(prev,curr)          
    return self.get_percent_of(pdff,self._sysdiff()) 
