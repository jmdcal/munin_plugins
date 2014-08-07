from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE

class cpu_usage_snsr(sensor):
  label='cpu usage (%)'
  cache='%s/processesprocess'%CACHE
  sys_mtd='cpu_times'
  proc_mtd='get_cpu_times'
  graph="AREASTACK"
  _properties={}
  
  def _evaluate(self,cache_id,curr):    
    prev=self.getValue(cache_id,curr)    
    pdff=self._mkdiff(prev,curr)          
    return get_percent_of(pdff,self._sysdiff()) 


def get_percent_of(val,full):
  try:
    percent = (val / full) * 100
  except ZeroDivisionError:
    # interval was too low
    percent = 0.0
  return percent
    